#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Dimitri Staessens <dimitri.staessens@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#    Nick Aerts        <nick.aerts@ugent.be>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#
import os
from time import sleep
import docker
import subprocess

import rumba.model as mod
import rumba.log as log
from rumba.executors.docker import DockerExecutor

logger = log.get_logger(__name__)

class Testbed(mod.Testbed):
    """
    Represents a docker testbed.
    """
    def __init__(self, exp_name, base_image, pull_image=True,
                 use_ovs=False):
        """
        Initializes the testbed class.

        :param exp_name: The experiment name.
        :param base_image: The docker base image.
        :param pull_image: Retrieve the docker image from the Docker hub?
        :param use_ovs: Use the OVS switch instead of the Linux bridge?
        """
        mod.Testbed.__init__(self, exp_name, "", "", "")

        img = base_image.rsplit(":", 1)

        self.base_image_repo = img[0]
        self.base_image_tag = "latest" if len(img) == 1 else img[1]
        self.base_image = "%s:%s" % (self.base_image_repo, self.base_image_tag)
        self.pull_image = pull_image
        self.use_ovs = use_ovs

        self.running_containers = {}
        self.active_bridges = set()
        self.active_ipcps = set()

        self.docker_client = docker.from_env()
        self.executor = DockerExecutor(self)

    def _swap_in(self, experiment):
        docker_client = self.docker_client

        # Pull image
        if self.pull_image:
                docker_client.images.pull(self.base_image_repo,
                                          self.base_image_tag)

        docker_client.images.get("%s:%s" % (self.base_image_repo,
                                            self.base_image_tag))

        # Start all nodes
        for node in experiment.nodes:
            self.running_containers[node.name] = docker_client.containers.run(
                self.base_image, command=node.startup_command, name=node.name,
                detach=True, network="none", privileged=True,
                devices=["/dev/fuse"])

        logger.info("Nodes starting")

        if not os.path.exists("/var/run/netns"):
            subprocess.check_call('sudo mkdir /var/run/netns'.split())

        for shim in experiment.dif_ordering:
            if not isinstance(shim, mod.ShimEthDIF):
                # Nothing to do here
                continue

            cmd = ""
            if self.use_ovs:
                cmd += 'sudo ovs-vsctl add-br %(shim)s'
            else:
                cmd += 'sudo ip link add %(shim)s type bridge'
            cmd = cmd % {'shim': shim.name}

            self.active_bridges.add(shim.name)

            subprocess.check_call(cmd.split())

            if not self.use_ovs:
                cmd = 'sudo ip link set dev %(shim)s up' % {'shim': shim.name}
                subprocess.check_call(cmd.split())
        for node in experiment.nodes:
            container = self.running_containers[node.name]

            container.reload()

            state = container.attrs["State"]

            while not state["Running"]:
                sleep(0.2)
                container.reload()
                state = container.attrs["State"]

            pid = state["Pid"]

            subprocess.check_call(('sudo ln -s /proc/%(pid)i/ns/net '
                             '/var/run/netns/%(pid)i' % {'pid': pid}).split())

            for ipcp in node.ipcps:
                if isinstance(ipcp, mod.ShimEthIPCP):
                    if ipcp.ifname is None:
                        ipcp.ifname = "eth%i" % node.ipcps.index(ipcp)

                    cmd = ('sudo ip link add %(node)s.%(ifname)s type veth '
                           'peer name _%(node)s.%(ifname)s'\
                           % {'node': node.name, 'ifname': ipcp.ifname})
                    subprocess.check_call(cmd.split())

                    cmd = ""
                    if self.use_ovs:
                        cmd += ('sudo ovs-vsctl add-port %(dif)s %(node)s.%('
                               'ifname)s')
                    else:
                        cmd += ('sudo ip link set %(node)s.%(ifname)s master '
                               '%(dif)s')

                    cmd = (cmd % {'node': node.name,
                                 'ifname': ipcp.ifname,
                                 'dif': ipcp.dif.name})

                    subprocess.check_call(cmd.split())

                    cmd = ('sudo ip link set _%(node)s.%(ifname)s '
                           'netns %(pid)i '
                           'name %(ifname)s'
                           % {'node': node.name,
                              'pid': pid,
                              'ifname': ipcp.ifname})
                    subprocess.check_call(cmd.split())

                    cmd = ('sudo ip link set dev %(node)s.%(ifname)s up'
                           % {'node': node.name, 'ifname': ipcp.ifname})
                    subprocess.check_call(cmd.split())

                    cmd = ('sudo ip netns exec %(pid)i ip link set dev '
                           '%(ifname)s up'
                           % {'pid': pid, 'ifname': ipcp.ifname})
                    subprocess.check_call(cmd.split())

                    self.active_ipcps.add(ipcp)

        logger.info("Experiment swapped in")

    def _swap_out(self, experiment):
        for name, container in self.running_containers.items():
            container.remove(force=True)

        for shim in experiment.dif_ordering:
            if isinstance(shim, mod.ShimEthDIF) and shim.name in self.active_bridges:
                cmd = ""
                if self.use_ovs:
                    cmd += 'sudo ovs-vsctl del-br %(shim)s'
                else:
                    cmd += 'sudo ip link del %(shim)s'
                cmd = cmd % {'shim': shim.name}

                subprocess.check_call(cmd.split())

                self.active_bridges.remove(shim.name)

        for name, container in self.running_containers.items():
            pid = container.attrs["State"]["Pid"]

            cmd = 'sudo rm /var/run/netns/%(pid)i' % {'pid': pid}
            subprocess.check_call(cmd.split())

        self.running_containers = {}

        logger.info("Experiment swapped out")
