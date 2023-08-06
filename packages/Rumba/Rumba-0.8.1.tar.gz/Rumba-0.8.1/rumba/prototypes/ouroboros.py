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

import time
import subprocess

import rumba.ssh_support as ssh
import rumba.model as mod
import rumba.multiprocess as m_processing
import rumba.log as log
import rumba.testbeds.local as local
import rumba.testbeds.dockertb as docker


logger = log.get_logger(__name__)


class Experiment(mod.Experiment):
    """
    Represents an Ouroboros experiment.
    """
    def __init__(self, testbed, nodes=None,
                 git_repo='git://ouroboros.ilabt.imec.be/ouroboros',
                 git_branch='master'):
        """
        Initializes the experiment class.

        :param testbed: The testbed to run the experiment on.
        :param nodes: The list of nodes.
        :param git_repo: The git repository to use for installation.
        :param git_branch: The branch of the git repository to use.
        """
        mod.Experiment.__init__(self, testbed, nodes, git_repo, git_branch)
        self.r_ipcps = dict()

        self.set_startup_command("irmd")

    @staticmethod
    def make_executor(node, packages, testbed):
        def executor(commands):
            ssh.aptitude_install(testbed, node, packages)
            node.execute_commands(commands, time_out=None, use_proxy=True)
        return executor

    def prototype_name(self):
        return 'ouroboros'

    def exec_local_cmd(self, cmd):
        try:
            logger.info(cmd)
            subprocess.check_call(cmd.split(' '))
        except subprocess.CalledProcessError as e:
            logger.error("Return code was " + str(e.returncode))
            raise

    def exec_local_cmds(self, cmds):
        for cmd in cmds:
            self.exec_local_cmd(cmd)

    def setup_ouroboros(self):
        if isinstance(self.testbed, docker.Testbed):
            return

        if isinstance(self.testbed, local.Testbed):
            subprocess.check_call('sudo -v'.split())
            self.irmd = subprocess.Popen(["sudo", "irmd"])
            logger.info("Started IRMd, sleeping 2 seconds...")
            time.sleep(2)
        else:
            for node in self.nodes:
                node.execute_command("sudo nohup irmd > /dev/null &", time_out=None)

    def install_ouroboros(self):
        if isinstance(self.testbed, local.Testbed):
            return

        packages = ["cmake", "protobuf-c-compiler", "git", "libfuse-dev",
                    "libgcrypt20-dev", "libssl-dev"]

        fs_loc = '/tmp/prototype'

        cmds = ["sudo apt-get install libprotobuf-c-dev --yes || true",
                "sudo rm -r " + fs_loc + " || true",
                "git clone -b " + self.git_branch + " " + self.git_repo + \
                " " + fs_loc,
                "cd " + fs_loc + " && mkdir build && cd build && " +
                "cmake -DCMAKE_BUILD_TYPE=Debug -DIPCP_FLOW_STATS=True " +
                "-DCONNECT_TIMEOUT=60000 " +
                "-DREG_TIMEOUT=60000 -DQUERY_TIMEOUT=4000 .. && " +
                "sudo make install -j$(nproc)"]

        names = []
        executors = []
        args = []

        for node in self.nodes:
            executor = self.make_executor(node, packages, self.testbed)
            names.append(node.name)
            executors.append(executor)
            args.append(cmds)
        m_processing.call_in_parallel(names, args, executors)

    def create_ipcps(self):
        for node in self.nodes:
            cmds = list()
            for ipcp in node.ipcps:
                cmds2 = list()
                if ipcp.dif_bootstrapper:
                    cmd = "irm i b n " + ipcp.name
                else:
                    cmd = "irm i c n " + ipcp.name

                if isinstance(ipcp.dif, mod.ShimEthDIF):
                    if isinstance(self.testbed, local.Testbed):
                        cmd += " type local layer " + ipcp.dif.name
                    else:
                        cmd += " type eth-llc dev " + ipcp.ifname
                        cmd += " layer " + ipcp.dif.name
                elif isinstance(ipcp.dif, mod.NormalDIF):
                    cmd += " type normal"
                    if ipcp.dif_bootstrapper:
                        pols = ipcp.dif.policy.get_policies()
                        for comp in pols:
                            for pol in pols[comp]:
                                cmd += " " + comp + " " + pol
                        cmd += " layer " + ipcp.dif.name + " autobind"

                        cmd2 = "irm r n " + ipcp.name
                        for dif_b in node.dif_registrations[ipcp.dif]:
                            cmd2 += " layer " + dif_b.name
                        cmds2.append(cmd2)
                        cmd2 = "irm r n " + ipcp.dif.name
                        for dif_b in node.dif_registrations[ipcp.dif]:
                            cmd2 += " layer " + dif_b.name
                        cmds2.append(cmd2)
                elif isinstance(ipcp.dif, mod.ShimUDPDIF):
                    # FIXME: Will fail, since we don't keep IPs yet
                    cmd += " type udp"
                    cmd += " layer " + ipcp.dif.name
                else:
                    logger.error("Unsupported IPCP type")
                    continue

                cmds.append(cmd)
                # Postpone registrations
                self.r_ipcps[ipcp] = cmds2

            node.execute_commands(cmds, time_out=None)

    def enroll_dif(self, el):
        for e in el:
            ipcp = e['enrollee']
            cmds = list()

            # Execute postponed registration
            if e['enroller'] in self.r_ipcps:
                e['enroller'].node.execute_commands(self.r_ipcps[e['enroller']],
                                                    time_out=None)
                self.r_ipcps.pop(e['enroller'], None)

            cmd = "irm r n " + ipcp.name
            for dif_b in e['enrollee'].node.dif_registrations[ipcp.dif]:
                cmd += " layer " + dif_b.name
            cmds.append(cmd)
            cmd = "irm i e n " + ipcp.name + " layer " + e['dif'].name + \
                  " autobind"
            cmds.append(cmd)
            cmd = "irm r n " + ipcp.dif.name
            for dif_b in e['enrollee'].node.dif_registrations[ipcp.dif]:
                cmd += " layer " + dif_b.name
            cmds.append(cmd)

            e['enrollee'].node.execute_commands(cmds, time_out=None)

    def setup_flows(self, el, comp):
        for e in el:
            ipcp = e['src']
            cmd = "irm i conn n " + ipcp.name + " comp " + \
                  comp + " dst " + e['dst'].name

            ipcp.node.execute_command(cmd, time_out=None)

    def _install_prototype(self):
        logger.info("Installing Ouroboros...")
        self.install_ouroboros()
        logger.info("Installed on all nodes...")

    def _bootstrap_prototype(self):
        logger.info("Starting IRMd on all nodes...")
        self.setup_ouroboros()
        logger.info("Creating IPCPs")
        self.create_ipcps()
        logger.info("Enrolling IPCPs...")

        for element, mgmt, dt in zip(self.enrollments,
                                     self.mgmt_flows,
                                     self.dt_flows):
            self.enroll_dif(element)
            self.setup_flows(mgmt, comp="mgmt")
            self.setup_flows(dt, comp="dt")

        logger.info("All done, have fun!")

    def _terminate_prototype(self):
        if isinstance(self.testbed, local.Testbed):
            logger.info("Killing IRMd...")
            subprocess.check_call('sudo killall -15 irmd'.split())
