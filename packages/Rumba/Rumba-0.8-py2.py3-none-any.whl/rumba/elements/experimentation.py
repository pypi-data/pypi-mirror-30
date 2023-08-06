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


import abc
import os
import shutil
import time

import rumba.log as log
import rumba.elements.topology as topology

logger = log.get_logger(__name__)


tmp_dir = '/tmp/rumba'


class Testbed(object):
    """
    Base class for every testbed plugin.
    """
    def __init__(self,
                 exp_name,
                 username,
                 password,
                 proj_name,
                 http_proxy=None,
                 system_logs=None):
        """
        :param exp_name: The experiment name.
        :param username: The username.
        :param password: The password.
        :param proj_name: The project name.
        :param http_proxy: HTTP proxy used by the testbed.
        :param system_logs: Location of the system logs of
                            images of the testbed.
        """
        self.username = username
        self.password = password
        self.proj_name = proj_name
        self.exp_name = exp_name
        self.http_proxy = http_proxy
        self.flags = {'no_vlan_offload': False}
        self.executor = None
        if system_logs is None:
            self.system_logs = ['/var/log/syslog']
        elif isinstance(system_logs, str):
            self.system_logs = [system_logs]
        else:
            self.system_logs = system_logs

    def swap_in(self, experiment):
        """
        Swaps experiment in on the testbed.

        :param experiment: The experiment.
        """
        for node in experiment.nodes:
            node.executor = self.executor

        self._swap_in(experiment)

        for dif in experiment.dif_ordering:
            if isinstance(dif, topology.ShimEthDIF):
                dif.link_quality.apply(dif)

    @abc.abstractmethod
    def _swap_in(self, experiment):
        logger.info("_swap_in(): nothing to do")

    def swap_out(self, experiment):
        """
        Swaps experiment out of the testbed.

        :param experiment: The experiment.
        """
        self._swap_out(experiment)

    @abc.abstractmethod
    def _swap_out(self, experiment):
        logger.info("swap_out(): nothing to do")


class Experiment(object):
    """
    Base class for experiments.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, testbed,
                 nodes=None,
                 git_repo=None,
                 git_branch=None,
                 log_dir=None,
                 prototype_logs=None):
        """
        :param testbed: The testbed of the experiment.
        :param nodes: The list of nodes in the experiment.
        :param git_repo: The git repository of the prototype.
        :param git_branch: The git branch of the repository.
        :param log_dir: Where to log output of the experiment.
        :param prototype_logs: Where the prototype logs its output.
        """
        if nodes is None:
            nodes = list()
        self.nodes = nodes
        self.git_repo = git_repo
        self.git_branch = git_branch
        self.testbed = testbed
        # the strategy employed for completing the enrollment phase in
        # the different DIFs
        self.enrollment_strategy = 'minimal'  # 'full-mesh', 'manual'
        # the strategy employed for setting up the data transfer
        # networks in the DIFs after enrollment
        self.dt_strategy = 'full-mesh'  # 'minimal', 'manual'
        self.dif_ordering = []
        self.enrollments = []  # a list of per-DIF lists of enrollments
        self.dt_flows = []  # a list of per-DIF lists of data transfer flows
        self.mgmt_flows = []  # a list of per-DIF lists of management flows

        # Determine log directory
        if log_dir is None:
            # If it is None, use /tmp/rumba/{project}
            # Wipe it and make it again
            exp_name = self.testbed.exp_name.replace('/', '_')  # Just in case
            log_dir = os.path.join(tmp_dir, exp_name)
            shutil.rmtree(log_dir, ignore_errors=True)
            os.mkdir(log_dir)
        self.log_dir = log_dir
        if not os.path.isdir(self.log_dir):
            raise Exception('Destination "%s" is not a directory. '
                            'Cannot fetch logs.'
                            % self.log_dir)
        self.prototype_logs = prototype_logs \
            if prototype_logs is not None else []

        # Generate missing information
        self.generate()

    def __repr__(self):
        s = ""
        for n in self.nodes:
            s += "\n" + str(n)

        return s

    def add_node(self, node):
        """
        Adds a node to the experiment.

        :param node: A node.
        """
        self.nodes.append(node)
        self.generate()

    def del_node(self, node):
        """
        Deletes a node from the experiment.

        :param node: A node.
        """
        self.nodes.remove(node)
        self.generate()

    # Compute registration/enrollment order for DIFs
    def compute_dif_ordering(self):
        # Compute DIFs dependency graph, as both adjacency and incidence list.
        difsdeps_adj = dict()
        difsdeps_inc = dict()

        for node in self.nodes:
            for dif in node.difs:
                if dif not in difsdeps_adj:
                    difsdeps_adj[dif] = set()

            for upper in node.dif_registrations:
                for lower in node.dif_registrations[upper]:
                    if upper not in difsdeps_inc:
                        difsdeps_inc[upper] = set()
                    if lower not in difsdeps_inc:
                        difsdeps_inc[lower] = set()
                    if upper not in difsdeps_adj:
                        difsdeps_adj[upper] = set()
                    if lower not in difsdeps_adj:
                        difsdeps_adj[lower] = set()
                    difsdeps_inc[upper].add(lower)
                    difsdeps_adj[lower].add(upper)

        # Kahn's algorithm below only needs per-node count of
        # incident edges, so we compute these counts from the
        # incidence list and drop the latter.
        difsdeps_inc_cnt = dict()
        for dif in difsdeps_inc:
            difsdeps_inc_cnt[dif] = len(difsdeps_inc[dif])
        del difsdeps_inc

        # Init difsdeps_inc_cnt for those DIFs that do not
        # act as lower IPCPs nor upper IPCPs for registration
        # operations
        for node in self.nodes:
            for dif in node.difs:
                if dif not in difsdeps_inc_cnt:
                    difsdeps_inc_cnt[dif] = 0

        # Run Kahn's algorithm to compute topological
        # ordering on the DIFs graph.
        frontier = set()
        self.dif_ordering = []
        for dif in difsdeps_inc_cnt:
            if difsdeps_inc_cnt[dif] == 0:
                frontier.add(dif)

        while len(frontier):
            cur = frontier.pop()
            self.dif_ordering.append(cur)
            for nxt in difsdeps_adj[cur]:
                difsdeps_inc_cnt[nxt] -= 1
                if difsdeps_inc_cnt[nxt] == 0:
                    frontier.add(nxt)
            difsdeps_adj[cur] = set()

        circular_set = [dif for dif in difsdeps_inc_cnt
                        if difsdeps_inc_cnt[dif] != 0]
        if len(circular_set):
            raise Exception("Fatal error: The specified DIFs topology"
                            "has one or more"
                            "circular dependencies, involving the following"
                            " DIFs: %s" % circular_set)

        logger.debug("DIF topological ordering: %s", self.dif_ordering)

    # Compute all the enrollments, to be called after compute_dif_ordering()
    def compute_enrollments(self):
        dif_graphs = dict()
        self.enrollments = []
        self.mgmt_flows = []
        self.dt_flows = []

        for dif in self.dif_ordering:
            neighsets = dict()
            dif_graphs[dif] = dict()
            first = None

            # For each N-1-DIF supporting this DIF, compute the set of nodes
            # that share such N-1-DIF. This set will be called the 'neighset' of
            # the N-1-DIF for the current DIF.

            for node in self.nodes:
                if dif in node.dif_registrations:
                    dif_graphs[dif][node] = []  # init for later use
                    if first is None:  # pick any node for later use
                        first = node
                    for lower_dif in node.dif_registrations[dif]:
                        if lower_dif not in neighsets:
                            neighsets[lower_dif] = []
                        neighsets[lower_dif].append(node)

            # Build the graph, represented as adjacency list
            for lower_dif in neighsets:
                # Each neighset corresponds to a complete (sub)graph.
                for node1 in neighsets[lower_dif]:
                    for node2 in neighsets[lower_dif]:
                        if node1 != node2:
                            dif_graphs[dif][node1].append((node2, lower_dif))

            self.enrollments.append([])
            self.dt_flows.append([])
            self.mgmt_flows.append([])

            if first is None:
                # This is a shim DIF, nothing to do
                continue

            er = []
            for node in dif_graphs[dif]:
                for edge in dif_graphs[dif][node]:
                    er.append("%s --[%s]--> %s" % (node.name,
                                                   edge[1].name,
                                                   edge[0].name))
            logger.debug("DIF graph for %s: %s", dif, ', '.join(er))

            # To generate the list of mgmt flows, minimal enrollments
            # and minimal dt flows, we simulate it, using
            # breadth-first traversal.
            enrolled = {first}
            frontier = {first}
            while len(frontier):
                cur = frontier.pop()
                for edge in dif_graphs[dif][cur]:
                    if edge[0] not in enrolled:
                        enrolled.add(edge[0])
                        enrollee = edge[0].get_ipcp_by_dif(dif)
                        assert(enrollee is not None)
                        enroller = cur.get_ipcp_by_dif(dif)
                        assert(enroller is not None)
                        if self.enrollment_strategy == 'minimal':
                            self.enrollments[-1].append({'dif': dif,
                                                         'enrollee': enrollee,
                                                         'enroller': enroller,
                                                         'lower_dif': edge[1]})
                        self.mgmt_flows[-1].append({'src': enrollee,
                                                    'dst': enroller})
                        if self.dt_strategy == 'minimal':
                            self.dt_flows[-1].append({'src': enrollee,
                                                      'dst': enroller})
                        frontier.add(edge[0])
            if len(dif.members) != len(enrolled):
                raise Exception("Disconnected DIF found: %s" % (dif,))

            # In case of a full mesh enrollment or dt flows
            for cur in dif_graphs[dif]:
                for edge in dif_graphs[dif][cur]:
                    if cur.name < edge[0].name:
                        enrollee = cur.get_ipcp_by_dif(dif)
                        assert(enrollee is not None)
                        enroller = edge[0].get_ipcp_by_dif(dif)
                        assert(enroller is not None)
                        if self.enrollment_strategy == 'full-mesh':
                            self.enrollments[-1].append({'dif': dif,
                                                         'enrollee': enrollee,
                                                         'enroller': enroller,
                                                         'lower_dif': edge[1]})
                        if self.dt_strategy == 'full-mesh':
                            self.dt_flows[-1].append({'src': enrollee,
                                                      'dst': enroller})

            if not (self.dt_strategy == 'minimal'
                    or self.dt_strategy == 'full-mesh') \
                    or not (self.enrollment_strategy == 'full-mesh'
                            or self.enrollment_strategy == 'minimal'):
                # This is a bug
                assert False

        log_string = "Enrollments:\n"
        for el in self.enrollments:
            for e in el:
                log_string += ("    [%s] %s --> %s through N-1-DIF %s\n"
                               % (e['dif'],
                                  e['enrollee'].name,
                                  e['enroller'].name,
                                  e['lower_dif']))
        logger.debug(log_string)

        log_string = "Mgmt flows:\n"
        for el in self.mgmt_flows:
            for e in el:
                log_string += ("    %s --> %s \n"
                               % (e['src'].name,
                                  e['dst'].name))
        logger.debug(log_string)

        log_string = "Dt flows:\n"
        for el in self.dt_flows:
            for e in el:
                log_string += ("    %s --> %s \n"
                               % (e['src'].name,
                                  e['dst'].name))
        logger.debug(log_string)

    def compute_ipcps(self):
        # For each node, compute the required IPCP instances, and associated
        # registrations
        for node in self.nodes:
            node.ipcps = []
            # We want also the node.ipcps list to be generated in
            # topological ordering
            for dif in self.dif_ordering:
                if dif not in node.difs:
                    continue

                # Create an instance of the required IPCP class
                ipcp = dif.get_ipcp_class()(
                    name='%s.%s' % (dif.name, node.name),
                    node=node, dif=dif)

                if dif in node.dif_registrations:
                    for lower in node.dif_registrations[dif]:
                        ipcp.registrations.append(lower)

                node.ipcps.append(ipcp)
                dif.ipcps.append(ipcp)

    def compute_bootstrappers(self):
        for node in self.nodes:
            for ipcp in node.ipcps:
                ipcp.dif_bootstrapper = True
                for el in self.enrollments:
                    for e in el:
                        if e['dif'] != ipcp.dif:
                            # Skip this DIF
                            break
                        if e['enrollee'] == ipcp:
                            ipcp.dif_bootstrapper = False
                            # Exit the loops
                            break
                    if not ipcp.dif_bootstrapper:
                        break

    def dump_ssh_info(self):
        f = open(os.path.join(tmp_dir, 'ssh_info'), 'w')
        for node in self.nodes:
            f.write("%s;%s;%s;%s;%s\n" % (node.name,
                                          self.testbed.username,
                                          node.ssh_config.hostname,
                                          node.ssh_config.port,
                                          node.ssh_config.proxy_server))
        f.close()

    # Examine the nodes and DIFs, compute the registration and enrollment
    # order, the list of IPCPs to create, registrations, ...
    def generate(self):
        start = time.time()
        self.compute_dif_ordering()
        self.compute_ipcps()
        self.compute_enrollments()
        self.compute_bootstrappers()
        for node in self.nodes:
            logger.info("IPCPs for node %s: %s", node.name, node.ipcps)
        end = time.time()
        logger.info("Layer ordering computation took %.2f seconds", end - start)

    def install_prototype(self):
        """
        Installs the prototype on the nodes.
        """
        start = time.time()
        self._install_prototype()
        end = time.time()
        logger.info("Install took %.2f seconds", end - start)

    def set_startup_command(self, command):
        for node in self.nodes:
            node.startup_command = command

    def bootstrap_prototype(self):
        """
        Bootstraps the prototype on the nodes.
        """
        start = time.time()
        self._bootstrap_prototype()
        end = time.time()
        logger.info("Bootstrap took %.2f seconds", end - start)

    @abc.abstractmethod
    def _install_prototype(self):
        raise Exception('install_prototype() method not implemented')

    @abc.abstractmethod
    def _bootstrap_prototype(self):
        raise Exception('bootstrap_prototype() method not implemented')

    @abc.abstractmethod
    def prototype_name(self):
        raise Exception('prototype_name() method not implemented')

    @abc.abstractmethod
    def _terminate_prototype(self):
        raise Exception('terminate_prototype() method not implemented')

    def swap_in(self):
        """
        Swap the experiment in on the testbed.
        """
        start = time.time()
        self.testbed.swap_in(self)
        self.dump_ssh_info()
        end = time.time()
        logger.info("Swap-in took %.2f seconds", end - start)

    def swap_out(self):
        """
        Swap the experiment out of the testbed.
        """
        start = time.time()
        # Terminate prototype gracefully
        self._terminate_prototype()
        for node in self.nodes:
            if node.ssh_config.client is not None:
                node.ssh_config.client.close()
            if node.ssh_config.proxy_client is not None:
                node.ssh_config.proxy_client.close()
        # Undo the testbed (testbed-specific)
        self.testbed.swap_out(self)
        end = time.time()
        logger.info("Swap-out took %.2f seconds", end - start)


class Executor:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute_command(self, node, command, as_root=False, time_out=3):
        # Execute command on a node
        return

    def execute_commands(self, node, commands, as_root=False, time_out=3):
        for command in commands:
            self.execute_command(node, command, as_root, time_out)

    @abc.abstractmethod
    def copy_file(self, node, path, destination):
        return

    def copy_files(self, node, paths, destination):
        for path in paths:
            self.copy_file(node, path, destination)

    @abc.abstractmethod
    def fetch_file(self, node, path, destination, sudo=False):
        return

    def fetch_files(self, node, paths, destination, sudo=False):
        for path in paths:
            self.fetch_file(node, path, destination, sudo)
