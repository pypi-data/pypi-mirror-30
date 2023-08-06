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

# Base class for client apps
#
# @ap: Application Process binary
# @options: Options to pass to the binary
#
import functools
import math
import os
import random
import time
import uuid

import rumba.model as model
import rumba.ssh_support as ssh_support
import rumba.log as log

try:
    from io import StringIO
except ImportError:
    import StringIO  # Python 2 here

logger = log.get_logger(__name__)

try:
    from numpy.random import poisson as _poisson
    from numpy.random import exponential as _exponential
    logger.debug("Using numpy for faster and better random variables.")
except ImportError:
    from rumba.recpoisson import poisson as _poisson

    def _exponential(mean_duration):
        return random.expovariate(1.0 / mean_duration)

    logger.debug("Falling back to simple implementations.")
    # PROBLEM! These logs will almost never be printed...
    # But we might not care


class _SBEntity(object):

    def __init__(self, e_id):
        self.id = e_id

    def get_e_id(self):
        return type(self).__name__ + '.' + self.id


class Client(_SBEntity):
    """
    Class representing a client application running in the experiment.

    A list of "client nodes" can be specified: if so, when generating a
    random script, this Client will be run only on those nodes.
    """

    current_id = -1

    @classmethod
    def _get_id(cls):
        cls.current_id += 1
        return cls.current_id

    def __init__(self, ap, nodes=None, options=None,
                 shutdown="kill <pid>", c_id=None):
        """
        :param ap: the application binary/command to be run
        :type ap: `str`
        :param nodes: the list of nodes on which the client should be run
        :type nodes: `:py:class:`rumba.model.Node` or `list` thereof
        :param options: the options to be passed to the binary or command
        :type options: `str`
        :param shutdown: the command to be run in order to stop the client.
                         The token "<pid>" will be changed into the process'
                         pid.
        :type shutdown: `str`
        :param c_id: the ID used to reference to this instance
        :type c_id: `str`
        """
        self.ap = ap
        e_id = c_id if c_id is not None else self.ap.replace(' ', '_')
        super(Client, self).__init__(e_id)
        self.startup = (ap + ((" " + options) if options is not None else ""))
        if isinstance(nodes, model.Node):
            nodes = [nodes]
        elif nodes is None:
            nodes = []
        self.nodes = nodes
        self.shutdown = shutdown

    def add_node(self, node):
        """
        Add a node to this instance's list.

        :param node: the node to add
        :type node: `rumba.model.Node`
        """
        if not isinstance(node, model.Node):
            raise Exception("A Node is required.")
        self.nodes.append(node)

    def process(self, duration, node=None, proc_id=None):
        """
        Generates a `.ClientProcess` of this application.

        :param duration: the duration of the process. It will be
                         passed to the process call in stead of the
                         <duration> token.
        :type duration: `float`
        :param node: the node on which the process should be run.
                     If `None`, a random node from this client's list
                     will be picked.
        :type node: `rumba.model.Node`
        :param proc_id: the ID used to reference to the generated process
        :type proc_id: `str`
        :return: the generated process
        :rtype: `.ClientProcess`
        """
        if proc_id is None:
            proc_id = "%s_%s" % (self.id, self._get_id())
        if node is None:
            if len(self.nodes) == 0:
                raise ValueError('No nodes for client %s'
                                 % (self.id,))
            node = random.choice(self.nodes)
        return ClientProcess(
            proc_id,
            self.id,
            self.startup,
            duration,
            node,
            self.shutdown
        )


class ClientProcess(_SBEntity):
    """Class representing a running client application process on a node"""
    def __init__(self, proc_id, ap_id, startup, duration,
                 node, shutdown="kill <pid>"):
        """

        :param proc_id: the ID used to identify this instance
        :type proc_id: `str`
        :param ap_id: the ID of the client app that generated this process
        :type ap_id: `str`
        :param startup: the full command used to start this process
        :type startup: `str`
        :param duration: the intended duration of this process. It will also
                         replace the "<duration>" token in the
                         `startup` parameter
        :type duration: `int` od `float`
        :param node: the node on which this process runs
        :type node: `rumba.model.Node`
        :param shutdown: the command used to stop this process
        :type shutdown: `str`
        """
        super(ClientProcess, self).__init__(proc_id)
        self.ap_id = ap_id
        self.startup = startup
        self.duration = duration if duration is not None else -1
        self.start_time = None
        self.running = False
        self.node = node
        self.pid = None
        self.shutdown = shutdown

    def run(self):
        """Starts this process"""
        if self.node is None:
            raise Exception('No node specified for client %s' % (self.ap_id,))
        self.start_time = time.time()

        logger.debug(
            'Starting client app %s on node %s with duration %s.',
            self.ap_id, self.node.name, self.duration
        )

        start_cmd = "./startup.sh %s %s" % (
            self.id,
            self.startup.replace("<duration>", str(self.duration)),
        )
        self.running = True
        try:
            self.pid = self.node.execute_command(start_cmd)
        except ssh_support.SSHException:
            logger.warning('Could not start client %s on node %s.',
                           self.ap_id, self.node.name)
        logger.debug('Client app %s on node %s got pid %s.',
                     self.ap_id, self.node.name, self.pid)

    def stop(self):
        """Stops this process"""
        if self.shutdown != "":
            logger.debug(
                'Killing client %s on node %s.',
                self.ap_id, self.node.name
            )
            try:
                kill_cmd = self.shutdown.replace('<pid>', str(self.pid))
                self.node.execute_command(kill_cmd)
            except ssh_support.SSHException:
                    logger.warn('Could not kill client %s on node %s.',
                                self.ap_id, self.node.name)
        else:
            logger.debug(
                'Client %s on node %s has terminated.',
                self.ap_id, self.node.name
            )


class Server(_SBEntity):
    """Class representing a server app running in the experiment"""

    current_id = -1

    @classmethod
    def get_id(cls):
        cls.current_id += 1
        return cls.current_id

    def __init__(self, ap, arrival_rate, mean_duration,
                 options=None, max_clients=float('inf'),
                 clients=None, nodes=None, min_duration=2, s_id=None):
        """

        :param ap: the application binary or command which should be run
        :type ap: `str`
        :param arrival_rate:
        :type arrival_rate: `float`
        :param mean_duration: the required average lifetime of a client
                              of this server
        :type mean_duration: `float`
        :param options: the options to be passed to the binary/command
                        starting this server
        :type options: `str`
        :param max_clients: the maximum number of simultaneous clients
                            which can be served by this application
        :type max_clients: `int`
        :param clients: the clients applications which will request to
                        be served by this application
        :type clients: `list` of `.Client`
        :param nodes: the list of nodes this server application
                      should be run on
        :type nodes: `list` of `rumba.model.Node`
        :param min_duration: the minimum lifetime of a client of this
                             server
        :type min_duration: `float`
        :param s_id: the ID used to identify this instance
        :type s_id: `str`
        """
        self.ap = ap
        e_id = s_id if s_id is not None else self.ap.replace(' ', '_')
        super(Server, self).__init__(e_id)
        self.options = options if options is not None else ""
        self.max_clients = max_clients
        if clients is None:
            clients = list()
        self.clients = clients
        if nodes is None:
            nodes = []
        self.nodes = nodes
        self.arrival_rate = arrival_rate  # mean requests/s
        self.actual_parameter = max(mean_duration - min_duration, 0.1)
        # in seconds
        self.pids = {}
        self.min_duration = min_duration

    def add_client(self, client):
        """
        Adds a client to this server's list

        :param client: the client to add
        :type client: `.Client`
        """
        self.clients.append(client)

    def del_client(self, client):
        """
        Removes a client from this server's list

        :param client: the client to remove
        :type client: `.Client`
        """
        self.clients.remove(client)

    def add_node(self, node):
        """
        Adds a node to this server's list

        :param node: the node to add
        :type node: `rumba.model.Node`
        """
        self.nodes.append(node)

    def del_node(self, node):
        """
        Removes a node from this server's list

        :param node: the node to remove
        :type node: `rumba.model.Node`
        """
        self.nodes.remove(node)

    def _get_new_clients(self, interval):
        """
        Returns a list of clients of size appropriate to the server's rate.

        The list's size should be a sample ~ Poisson(arrival_rate) over
        interval seconds.
        Hence, the average size should be interval * arrival_rate.

        :param interval: the time increment for which new clients should be
                         generated
        :type interval: `float`

        :return: the list of new clients to be started
        :rtype: `list` of `(duration, node, proc_id, client)` tuples
        """
        number = _poisson(self.arrival_rate * interval)
        number = int(min(number, self.max_clients))
        return [self._make_process_arguments() for _ in range(number)]

    def _get_duration(self):
        return _exponential(self.actual_parameter) + self.min_duration

    def _make_process_arguments(self, duration=None, node=None,
                                proc_id=None, client=None):
        if len(self.clients) == 0:
            raise Exception("Server %s has empty client list." % (self,))
        if duration is None:
            duration = self._get_duration()
        if client is None:
            client = random.choice(self.clients)
        if node is None:
            node = random.choice(client.nodes)
        if proc_id is None:
            proc_id = "%s_%s" % (client.ap, client._get_id())
        return duration, node, proc_id, client

    def make_client_process(self, duration=None, node=None,
                            proc_id=None, client=None):
        """
        Returns a process of a client application of this server.

        Any parameter left as `None` will be randomly generated
        according to the parameters assigned to this server and its
        clients.

        :param duration: the lifetime of the process
        :type duration: `float`
        :param node: the node on which the process should be run
        :type node: `rumba.model.Node`
        :param proc_id: the ID identifying the returned process
        :type proc_id: `str`
        :param client: the client of which the returned process
                       should be an instance
        :type client: `.Client`
        :return: the process
        :rtype: `.ClientProcess`
        """
        (d, n, p, c) = self._make_process_arguments(duration, node,
                                                    proc_id, client)
        return c.process(
            duration=float("%.2f" % (d,)),
            node=n,
            proc_id=p
        )

    def run(self):
        """Starts this server"""
        for node in self.nodes:
            run_cmd = self.ap + (
                (" " + self.options) if self.options is not None else ""
            )
            cmd_2 = "./startup.sh %s %s" % ('server_' + self.id, run_cmd)
            logger.debug(
                'Starting server %s on node %s.',
                self.id, node.name
            )
            try:
                self.pids[node] = node.execute_command(cmd_2)
            except ssh_support.SSHException:
                logger.warn('Could not start server %s on node %s.',
                            self.id, node.name)

    def stop(self):
        """Stops this server"""
        for node, pid in self.pids.items():
            logger.debug(
                'Killing server %s on node %s.',
                self.id, node.name
            )
            try:
                node.execute_command("kill %s" % pid)
            except ssh_support.SSHException:
                logger.warn('Could not kill server %s on node %s.',
                            self.id, node.name)


# Base class for ARCFIRE storyboards
#
# @experiment: Experiment to use as input
# @duration: Duration of the whole storyboard
# @servers: App servers available in the network.
#           Type == Server or Type == List[Tuple[Server, Node]]
#
class StoryBoard(_SBEntity):
    """Class representing the storyboard of an experiment"""

    SCRIPT_RESOLUTION = 0.1
    EXECUTION_RESOLUTION = 2.5  # in seconds (may be a float)

    def get_e_id(self):
        return 'storyboard'

    def __init__(self, duration, experiment=None, servers=None):
        """

        :param duration: the required duration of the storyboard (s)
        :type duration: `float`
        :param experiment: the experiment data this storyboard should use
        :type experiment: `rumba.model.Experiment`
        :param servers: the list of servers this storyboard will use to generate
                        random events through the
                        :meth:`.StoryBoard.generate_script` method
        :type servers: list of `.Server` or (`.Server`, `rumba.model.Node`)
                       tuples
        """
        self.id = 'storyboard'
        self.experiment = experiment
        self.duration = duration
        self.cur_time = 0.0
        self.server_apps = {}
        self.client_apps = {}
        if servers is None:
            servers = list()
        for s in servers:
            self._validate_and_add_server(s)
        self.client_nodes = set()
        self.server_nodes = set()
        self.process_dict = {}
        self.active_clients = self.process_dict.values()
        self.start_time = None
        self.commands_list = {}
        self.node_map = {}
        self.shims = {}
        self._build_nodes_lists()
        # The following must be last, because it needs the info from
        # _build_nodes_list
        self._script = _Script(self)

    def _build_nodes_lists(self):
        """Populates server_nodes and client_nodes lists"""
        for server in self.server_apps.values():
            for node in server.nodes:
                self.server_nodes.add(node)
            for client in server.clients:
                for node in client.nodes:
                    self.client_nodes.add(node)
        if self.experiment is not None:
            for node in self.experiment.nodes:
                self.node_map[node.name] = node
            for dif in self.experiment.dif_ordering:
                if isinstance(dif, model.ShimEthDIF):
                    self.shims[dif.name] = dif

    def _validate_and_add_server(self, s, n=None):
        if len(s.clients) == 0:
            logger.warning("'%s' server has no registered clients.", s.ap)
        else:
            for client in s.clients:
                self.client_apps[client.id] = client
        if n is not None:
            s.add_node(n)
        else:
            if len(s.nodes) == 0:
                logger.warning("'%s' server has no registered nodes.", s.ap)
        for node in s.nodes:
            if node not in self.experiment.nodes:
                raise ValueError('Cannot run server on node %s, '
                                 'not in experiment.' % (node.name,))
        self.server_apps[s.id] = s
        self._build_nodes_lists()

    def set_experiment(self, experiment):
        """
        Set the storyboard's underlying experiment instance

        :param experiment: the experiment instance
        :type experiment: `rumba.model.Experiment`
        """
        if not isinstance(experiment, model.Experiment):
            raise TypeError('Experiment instance required.')
        self.experiment = experiment
        self._build_nodes_lists()

    def add_server(self, server):
        """
        Register a server application to the sb for
        random event generation.

        :param server: the server application
        :type server: `.Server`
        """
        if self.experiment is None:
            raise ValueError("Cannot add a server before "
                             "setting the experiment.")
        if not isinstance(server, Server):
            raise TypeError('Argument must be of type Server')
        self._validate_and_add_server(server)

    def add_server_on_node(self, server, node):
        """
        Simultaneously add a server to this storyboard
        and a node to the server.

        :param server: the server to be added to the storyboard
        :type server: `.Server`
        :param node: the node upon which the server should run
        :type node: `rumba.model.Node`
        """
        if self.experiment is None:
            raise ValueError("Cannot add a server before "
                             "setting the experiment.")
        if not isinstance(server, Server):
            raise TypeError('First argument must be of type Server')
        if not isinstance(node, model.Node):
            raise TypeError('Second argument must be of type Node')
        self._validate_and_add_server(server, node)

    def del_server(self, server):
        """
        Deregister a server application from this storyboard.

        :param server: the server to remove
        :type server: `.Server`
        """
        del self.server_apps[server.id]
        self._build_nodes_lists()

    def schedule_action(self,
                        call,
                        args=None,
                        kwargs=None,
                        c_time=None,
                        trigger=None,
                        ev_id=None,):
        """
        Calls a Python function with the specified arguments as soon as
        the specified triggers are satisfied.

        :param call: the function to run
        :type  call: `callable`
        :param args: arguments to pass to the function
        :type args: `list`
        :param kwargs: keyword arguments to be passed
        :type kwargs: `dict`
        :param c_time: the function will not be called before `c_time`
                       seconds have passed
        :type c_time: `float`
        :param trigger: the function must not be called before the event
                        `trigger` has completed
        :type trigger: `.Event` or `str`
        :param ev_id: the ID to assign to the generated event
        :type  ev_id: `str`
        :return: the event representing the calling of the function
        :rtype: `.Event`
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        action = functools.partial(call, *args, **kwargs)
        event = Event(action, ev_id=ev_id, ev_time=c_time, trigger=trigger)
        self.add_event(event)
        return event

    def schedule_command(self, t, node, command):
        """
        Schedules the given command to be run no sooner than t seconds
        from the start of the storyboard execution.

        Commands triggering at times very close to each other might be
        run in any order. Use the :meth:`.StoryBoard.schedule_action` method
        to force a command to run after another event.

        :param t: seconds to wait before running the command
        :type t: `float`
        :param node: the node on which the command should be run
        :type node: `rumba.model.Node` or `str`
        :param command: the command(s) to be run
        :type command: `str` or `list` of `str`
        """
        if self.experiment is None:
            raise ValueError("An experiment is needed to schedule commands.")
        if self._script is None:
            self._script = _Script(self)
        if isinstance(node, str):
            node = self.node_map[node]
        if node not in self.experiment.nodes:
            raise ValueError('Cannot run command on node %s, '
                             'not in experiment.' % (node.name,))
        if isinstance(command, str):
            command = [command]
        action = functools.partial(self.run_command, node, command)
        self._script.add_event(Event(action, ev_time=t))

    def run_command(self, node, command):
        """
        Runs a command (or several) on a given node, immediately.

        :param node: the node on which the command should be run
        :type node: `rumba.model.Node` or `str`
        :param command: the command(s) to be run
        :type command: `str` or `list` of `str`
        """
        if self.experiment is None:
            raise ValueError("Experiment needed to run commands.")
        if isinstance(node, str):
            node = self.node_map[node]
        if node not in self.experiment.nodes:
            raise ValueError('Cannot run command on node %s, '
                             'not in experiment.' % (node.name,))
        if isinstance(command, str):
            command = [command]
        node.execute_commands(command)

    def add_event(self, event):
        """
        Adds an event to this script.

        The event acan be passed either as an `.Event`
        instance or as a string as read as from a .rsb script.

        :param event: the event to add
        :type event: `.Event` or `str`
        """
        self._script.add_event(event)

    def del_event(self, event):
        """
        Remove an event from this storyboard

        :param event: the event (or id thereof) to remove
        :type event: `.Event` or `str`
        """
        self._script.del_event(event)

    def run_client_of(self,
                      server,
                      duration=None,
                      node=None,
                      proc_id=None,
                      callback=None):
        """
        Runs a random client of the specified server
        with the specified parameters.

        Except for the server, if a parameter is not specified,
        it will be randomly generated according to the server
        parameters (mean duration, registered client apps
        and their nodes)

        :param server: the server of which one client should be run
        :type server: `.Server`
        :param duration: the duration of the client process
        :type duration: `float`
        :param node: the node on which the client should be run
        :type node: `rumba.model.Node` or `str`
        :param proc_id: the ID identifying the generated process
        :type proc_id: `str`
        :param callback: callable or list thereof to be run
                         after client termination
        :type callback: `callable` or `list` of `callable`
        """
        if isinstance(server, str):
            server = self.server_apps[server]
        if duration is None:
            duration = server._get_duration()
        client = random.choice(server.clients)
        self.run_client(client, duration, node, proc_id, callback)

    def run_client(self,
                   client,
                   duration,
                   node=None,
                   proc_id=None,
                   callback=None):
        """
        Runs the specified client app with the specified parameters.

        If the node parameter is not given, it will be chosen at random
        among the client default nodes.

        :param client: the client which should be run
        :type client: `.Client`
        :param duration: the duration of the client process
        :type duration: `float`
        :param node: the node on which the client should be run
        :type node: `rumba.model.Node` or `str`
        :param proc_id: the entity ID to use for the process
        :type proc_id: `str`
        :param callback: callable or list thereof to be run
                         after client termination
        :type callback: `callable` or `list` of `callable`
        """
        if isinstance(client, str):
            client = self.client_apps[client]
        if node is None:
            if len(client.nodes) == 0:
                raise ValueError('No nodes registered for client %s',
                                 client.id)
            node = random.choice(client.nodes)
        elif isinstance(node, str):
            node = self.node_map[node]
        if callback is None:
            callback = []
        elif not hasattr(callback, '__len__'):
            callback = [callback]
        process = client.process(duration, node, proc_id)
        self.process_dict[process.id] = process
        process.run()
        action = functools.partial(self.kill_process, process.id)
        term_ev = Event(action, ev_time=(self.cur_time + duration))
        self.add_event(term_ev)
        for cb in callback:
            cb_event = Event(action=cb, trigger=term_ev)
            self.add_event(cb_event)

    def start_client_of(self, server, duration=None, node=None, proc_id=None):
        """
        Starts a random client of the specified server
        with the specified parameters.

        Except for the server and the duration, if a parameter
        is not specified, it will be randomly generated according
        to the server parameters (client apps and their nodes).

        Note that this method, as opposed to
        :meth:`.StoryBoard.run_client_of`, will not automatically generate
        an event stopping the client after the duration is expired.
        In most cases, :meth:`.StoryBoard.run_client_of` is the way to go.

        :param server: the server of which one client should be run
        :type server: `.Server`
        :param duration: the duration of the client process
        :type duration: `float`
        :param node: the node on which the client should be run
        :type node: `rumba.model.Node` or `str`
        :param proc_id: the ID identifying the generated process
        :type proc_id: `str`
        """
        if isinstance(server, str):
            server = self.server_apps[server]
        client = random.choice(server.clients)
        self.start_client(client, duration, node, proc_id)

    def start_client(self, client, duration=None, node=None, proc_id=None):
        """
        Starts the specified client app with the specified parameters.

        If the node parameter is not given, it will be chosen at random
        among the client default nodes.

        Note that this method, as opposed to
        :meth:`.StoryBoard.run_client`, will not automatically generate
        an event stopping the client after the duration is expired.
        In most cases, :meth:`.StoryBoard.run_client` is the way to go.

        :param client: the client which should be run
        :type client: `.Client`
        :param duration: the duration of the client process
        :type duration: `float`
        :param node: the node on which the client should be run
        :type node: `rumba.model.Node` or `str`
        :param proc_id: the entity ID to use for the process
        :type proc_id: `str`
        """
        if isinstance(client, str):
            client = self.client_apps[client]
        if node is None:
            node = random.choice(client.nodes)
        process = client.process(duration, node, proc_id)
        self.process_dict[process.id] = process
        process.run()

    def kill_process(self, proc_id):
        """
        Stops the `.ClientProcess` with the specified ID.

        :param proc_id: the ID of the process to kill
        :type proc_id: `str`
        """
        process = self.process_dict.get(proc_id, None)
        if process is None:
            raise ValueError('No process named %s' % (proc_id,))
        process.stop()
        del self.process_dict[proc_id]

    def _periodic_check(self, t):
        self._script.check_for_ready_ev(t)
        self._script.run_ready()

    def generate_script(self, clean=True):
        """
        Randomly generate a script for this experiment based on the
        `.Server` instances registered to this storyboard,
        their nodes, thier clients and the nodes of their clients.

        :param clean: if `True`, discard the current script before
                      generating a new one.
        :type clean: `bool`
        """
        if self.experiment is None:
            raise ValueError('Cannot generate script without an experiment')
        if clean:
            self._script = _Script(self)
        t = self.SCRIPT_RESOLUTION
        marker = 5
        last_marker = 0
        while t < self.duration:
            if int(t) >= (last_marker+1)*marker:
                last_marker += 1
                logger.debug('Passed the %s seconds mark', last_marker*marker)
            for server in self.server_apps.values():
                c_l = server._get_new_clients(self.SCRIPT_RESOLUTION)
                for d, n, p, c in c_l:
                    if d > self.duration - t:  # would outlast the experiment
                        continue
                    start = self._make_process_events(
                        t,
                        d,
                        n,
                        p,
                        c
                    )
                    self._script.add_event(start)
            t += self.SCRIPT_RESOLUTION

    def _make_process_events(self, t, d, n, p, c):
        start_action = functools.partial(
            self.run_client,
            c,
            d,
            n,
            p
        )
        start_event = Event(start_action, ev_time=t)
        return start_event

    def start(self):
        """Start the storyboard execution."""
        if self.experiment is None:
            raise ValueError("Cannot run sb with no experiment.")
        if self._script is None:
            self.generate_script()
        logger.info('Starting storyboard execution')
        self._build_nodes_lists()
        logger.debug('Server nodes are: %s.',
                     [x.name for x in self.server_nodes])
        logger.debug('Command list is: %s.', {x: [(y.name, z)
                                                  for y, z in t]
                                              for (x, t)
                                              in self.commands_list.items()})
        self.start_time = time.time()
        script = r'logname="$1"; shift; nohup "${@}" ' \
                 r'> /tmp/${logname}.rumba.log 2>&1  & echo "$!"'
        logger.debug("Writing utility startup script on nodes.")
        for node in self.node_map.values():
            node.execute_command(
                "echo '%s' > startup.sh && chmod a+x startup.sh" % (script,)
            )
        try:
            for server in self.server_apps.values():
                server.run()
            res = self.SCRIPT_RESOLUTION  # for brevity
            while self.cur_time < self.duration:
                self._periodic_check(self.cur_time)
                next_breakpoint = math.ceil(self.cur_time / res) * res
                delta = next_breakpoint - self.cur_time
                if delta > 0:  # just in case
                    time.sleep(delta)
                self.cur_time = float(time.time() - self.start_time)
            self._periodic_check(self.cur_time)
            # Do things that were scheduled
            # in the last seconds
            # of the StoryBoard
        finally:  # Kill everything. No more mercy.
            for client in self.active_clients:
                client.stop()
            for server in self.server_apps.values():
                server.stop()

    def fetch_logs(self, local_dir=None):
        """
        Fetch all server application and client application logs from
        the different nodes, and put them into `local_dir`

        :param local_dir: the local directory in which the logs should
                          be stored. If `None`, `/tmp/rumba/<exp_name>`
                          will be used
        :type local_dir: `str`
        """
        if local_dir is None:
            local_dir = self.experiment.log_dir
        if not os.path.isdir(local_dir):
            raise Exception('Destination "%s" is not a directory. '
                            'Cannot fetch logs.'
                            % local_dir)
        for node in self.node_map.values():
            dst_dir = os.path.join(local_dir, node.name)
            if not os.path.isdir(dst_dir):
                os.mkdir(dst_dir)
            logs_list = node.execute_command('ls /tmp/*.rumba.log '
                                             '|| echo ""')
            logs_list = [x for x in logs_list.split('\n') if x != '']
            logger.debug('Log list is:\n%s', logs_list)
            node.fetch_files(logs_list, dst_dir)

    def schedule_link_state(self, t, dif, state):
        """
        Schedules a link's (`rumba.model.ShimEthDIF`) state to go
        up or down at the specified time.

        :param t: the time in the storyboard at which the state
                  change should happen
        :type t: `float`
        :param dif: the DIF which should be reconfigured
        :type dif: `rumba.model.ShimEthDIF`
        :param state: the desired state
        :type state: `str` -- either `up` or `down`
        """
        if self.experiment is None:
            raise ValueError("An experiment is needed to schedule commands.")
        if not isinstance(dif, model.ShimEthDIF):
            raise ValueError("Not a Shim Ethernet DIF.")
        if state not in ['up', 'down']:
            raise ValueError('Only possible states are "up" and "down"')

        if self._script is None:
            self._script = _Script(self)

        for node in dif.members:
            action = functools.partial(node.set_link_state, dif, state)
            self._script.add_event(Event(action, ev_time=t))

    def schedule_link_up(self, t, dif):
        """
        Schedules a link's (`rumba.model.ShimEthDIF`) state to go
        up at the specified time.

        :param t: the time in the storyboard at which the state
                  change should happen
        :type t: `float`
        :param dif: the DIF which should be reconfigured
        :type dif: `rumba.model.ShimEthDIF`
        """
        self.schedule_link_state(t, dif, 'up')

    def schedule_link_down(self, t, dif):
        """
        Schedules a link's (`rumba.model.ShimEthDIF`) state to go
        down at the specified time.

        :param t: the time in the storyboard at which the state
                  change should happen
        :type t: `float`
        :param dif: the DIF which should be reconfigured
        :type dif: `rumba.model.ShimEthDIF`
        """
        self.schedule_link_state(t, dif, 'down')

    def schedule_node_state(self, t, node, state):
        """
        Schedules a node's state to go up or down at the specified time.

        When a node is down all of its links are set to `down`.

        :param t: the time in the storyboard at which the state
                  change should happen
        :type t: `float`
        :param node: the node which should be reconfigured
        :type node: `rumba.model.Node`
        :param state: the desired state
        :type state: `str` -- either `up` or `down`
        """
        if self.experiment is None:
            raise ValueError("An experiment is needed to schedule commands.")

        if self._script is None:
            self._script = _Script(self)

        for dif in node.difs:
            if not isinstance(dif, model.ShimEthDIF):
                continue
            action = functools.partial(node.schedule_link_state, dif, state)
            self._script.add_event(Event(action, ev_time=t))

    def schedule_node_up(self, t, node):
        """
        Schedules a node's state to go up at the specified time.

        :param t: the time in the storyboard at which the state
                  change should happen
        :type t: `float`
        :param node: the node which should be reconfigured
        :type node: `rumba.model.Node`
        """
        self.schedule_node_state(t, node, 'up')

    def schedule_node_down(self, t, node):
        """
        Schedules a node's state to go down at the specified time.

        When a node is down all of its links are set to `down`.

        :param t: the time in the storyboard at which the state
                  change should happen
        :type t: `float`
        :param node: the node which should be reconfigured
        :type node: `rumba.model.Node`
        """
        self.schedule_node_state(t, node, 'down')

    def write_script(self, buffer):
        """
        Writes the script on a (string-oriented) buffer,
        at the current position

        :param buffer: a string buffer.
        :type buffer: string-oriented `file-like` object
        """
        self._script.write(buffer)

    def write_script_to_file(self, filename, clean=True):
        """
        Writes the script to a file.

        :param filename: the name of the destination file
        :type filename: `str`
        :param clean: if True, current file's contents will be overwritten.
                      If False, the script will be appended to the file.
        :type clean: `bool`
        """
        mode = 'w'
        if not clean:
            mode += '+'
        with open(filename, mode) as f:
            self.write_script(f)

    def write_script_string(self):
        """
        Writes the script as a string and returns it.

        :return: the script as a string.
        :rtype: `str`
        """
        s = StringIO()
        self.write_script(s)
        return s

    def parse_script(self, buffer, clean=True):
        """
        Reads a script from a buffer, at the current position.

        :param buffer: the buffer to read from.
        :type buffer: string-oriented `file-like` object
        :param clean: if True, discard the current script before reading.
        :type clean: `bool`
        """
        if clean:
            self._script = _Script(self)
        self._script.parse(buffer)

    def parse_script_file(self, filename, clean=True):
        """
        Reads a script from a file.

        :param filename: the file to read from.
        :type filename: `str`
        :param clean: if True, discard the current script before reading.
        :type clean: `bool`
        """
        if clean:
            self._script = _Script(self)
        with open(filename, 'r') as f:
            self.parse_script(f, clean)

    def parse_script_string(self, string, clean=True):
        """
        Reads a string as a script.

        :param string: the string to read from.
        :type string: `str`
        :param clean: if True, discard the current script before reading.
        :type clean: `bool`
        """
        if clean:
            self._script = _Script(self)
        buffer = StringIO(string)
        self.parse_script(buffer, clean)

    def capture_traffic(self, start, end, node, dif):
        """
        Captures the traffic of an interface on a node.

        :param start: the time to start capturing.
        :type start: `float`
        :param end: the time to stop capturing.
        :type end: `float`
        :param node: the node to capture on.
        :type node: `rumba.model.Node`
        :param dif: the node's Shim Ethernet DIF whose interface
                    will be used for the capture.
        :type dif: `rumba.model.ShimEthDIF`
        """
        for ipcp in dif.ipcps:
            if ipcp.node is not node:
                continue
            # In case tcpdump is not present, this assumes a testbed
            # with Ubuntu/Debian just like the rest of installation
            if not node.has_tcpdump:
                ssh_support.aptitude_install(self.experiment.testbed,
                                             node, ["tcpdump"])
                node.has_tcpdump = True

            # Create random string
            pcap_file = node.name + '_' + dif.name + '_' + \
                        str(uuid.uuid4())[0:4] + ".pcap"

            tcpd_client = Client(ap="tcpdump", options="-i %s -w %s" \
                                 % (ipcp.ifname, pcap_file))\
                .process(end-start, node, 'tcpdump_proc')

            self.schedule_action(tcpd_client.run, c_time=start)
            end_event = self.schedule_action(tcpd_client.stop, c_time=end)

            self.schedule_action(
                node.fetch_file,
                args=[pcap_file, self.experiment.log_dir],
                kwargs={'sudo': True},
                trigger=end_event
            )


class Event(object):
    """Class representing an event in a `.StoryBoard`"""

    cur_id = -1

    @classmethod
    def generate_id(cls):
        cls.cur_id += 1
        return "__event_%s" % (cls.cur_id,)

    def __init__(self, action, ev_id=None, ev_time=None, trigger=None):
        """
        :param ev_id: ID of the event
        :type ev_id: `str`
        :param action: action to undertake when event is activated
        :type action: nullary `callable`
        :param ev_time:  seconds to wait before running the event
        :type ev_time: `float`
        :param trigger: Event which must complete before
                        this event runs
        :type trigger: `.Event`
        """
        self.id = ev_id if ev_id is not None else self.generate_id()
        if ev_time is None and trigger is None:
            raise ValueError('No condition specified for event %s.' %
                             self.id)
        self.action = action
        self.time = ev_time
        self._trigger = trigger
        self.trigger = trigger.id if trigger is not None else None
        self.exception = None
        self.done = False
        self._repr = "%(prefix)s &%(label)s | %(entity)s %(method)s" % {
            'prefix': self._prefix_repr(),
            'label': self.id,
            'entity': '$' + self.action.func.__self__.get_e_id(),
            'method': self._action_repr()
        }

    def _action_repr(self):
        if isinstance(self.action, functools.partial):
            name = self.action.func.__name__
            args = ' '.join(self._action_arg_repr(x) for x in self.action.args)
        else:
            name = self.action.__name__
            args = ''
        return ' '.join((name, args))

    @staticmethod
    def _action_arg_repr(arg):
        if hasattr(arg, 'get_e_id'):
            return '$' + arg.get_e_id()
        elif isinstance(arg, str):
            return "'" + arg + "'"
        elif isinstance(arg, float):
            return "%.2f" % (arg,)
        else:
            return str(arg)  # Assuming int

    def _prefix_repr(self):
        conditions = []
        if self.time is not None:
            conditions.append("%.2f" % (self.time,))
        if self.trigger is not None:
            conditions.append(self.trigger)
        return ", ".join(conditions)

    @property
    def failed(self):
        """

        :return: True if this event's execution failed
        :rtype: `bool`
        """
        return self.exception is not None

    def pre_exec(self):  # hook to be overridden
        pass

    def post_exec(self):  # hook to be overridden
        pass

    def _start(self):
        self.pre_exec()
        if self.done:
            raise ValueError('Event %s has already ran' % self.id)

    def run(self):
        """Run this event's action"""
        self._start()
        try:
            self.action()
        except Exception as e:
            self.exception = e
        self._done()

    def check(self, cur_time):
        """
        Check if this event can be run, i.e. it's prerequisites are satisfied.

        :param cur_time: current elapsed time from storyboard's start.
        :type cur_time: `float`
        :return: True if the preconditions are satisfied, False otherwise.
        :rtype: `bool`
        """
        return \
            (self.time is None or cur_time > self.time) \
            and (self._trigger is None or self._trigger.done)

    def _done(self):
        self.done = True
        if self.exception is not None:
            logger.warning('Event %s failed. %s: %s.',
                           self.id,
                           type(self.exception).__name__,
                           str(self.exception))
        self.post_exec()

    def __str__(self):
        return self.id

    def __repr__(self):
        return self._repr


class _Script(object):

    def __init__(self, storyboard):
        if storyboard is None:
            raise ValueError("storyboard must not be None")
        self.events_by_id = {}
        self._waiting_events = {}
        self._events_ready = []

        self._nodes = {}
        self._servers = {}
        self._clients = {}
        self._storyboard = storyboard
        self._entities = {}
        self._parse_entities()

    @property
    def _experiment(self):
        return self._storyboard.experiment

    @property
    def _testbed(self):
        exp = self._experiment
        if exp is None:
            return None
        else:
            return exp.testbed

    def _parse_entities(self):
        self._nodes = self._storyboard.node_map
        self._servers = self._storyboard.server_apps
        self._clients = self._storyboard.client_apps
        self._processes = {}
        self._shims = self._storyboard.shims
        self._entities = {
            'sb': self._storyboard,
            'storyboard': self._storyboard,
            'testbed': self._testbed,
            'experiment': self._experiment,
            'Node': self._nodes,
            'Server': self._servers,
            'Client': self._clients,
            'ClientProcess': self._processes,
            'ShimEthDIF': self._shims
        }

    def add_process(self, process):
        self._processes[process.id] = process

    def add_event(self, event):
        """
        Add an event to this script
        @param event: (Event or str) the event to add
        """
        if isinstance(event, str):
            self._parse_line(event)
            return
        ev_id = event.id
        self.events_by_id[ev_id] = event
        self._waiting_events[ev_id] = event

    def del_event(self, event):
        """
        Remove an event from this script
        @param event: (Event or str) the event (or id thereof) to remove
        """
        if isinstance(event, Event):
            event = event.id
        del self.events_by_id[event]
        del self._events_ready[event]

    def check_for_ready_ev(self, cur_time):
        """
        Check which events are ready to run, and mark them
        @param (float) current time
        """
        new_wait = {}
        for i, e in self._waiting_events.items():
            if e.check(cur_time):
                self._events_ready.append(e)
            else:
                new_wait[i] = e
        self._waiting_events = new_wait

    def run_ready(self):
        """
        Run events marked as ready by a previous inspection

        (see @check_for_ready_ev)
        """
        while len(self._events_ready):
            event = self._events_ready.pop()
            logger.debug("Running event %s.", event.id)
            event.run()

    def _nested_iterator(self, d):
        for t in ((x, self.events_by_id[x])
                  for e_lst in d.values() for x in e_lst):
            yield t

    def _resolve_entity(self, e_id):
        e_key = e_id.split('.')
        result = self._entities
        while len(e_key) != 0:
            key = e_key.pop(0)
            result = result.get(key)
            if result is None:
                raise ValueError('Invalid entity key %s at %s'
                                 % (e_id, key))
        return result

    def _parse_action(self, entity, action_l):
        method_n = action_l[0]
        method = getattr(entity, method_n, None)
        if method is None:
            raise ValueError('No method called "%s" for entity %s.'
                             % (method_n, entity.get_e_id()))
        args_l = action_l[1:]
        args = self._parse_action_arguments(args_l)
        return functools.partial(method, *args)
        # TODO maybe some argument checking?

    def _parse_action_arguments(self, args_l):
        args = []
        quotes_part = None
        while len(args_l) > 0:
            arg_s = args_l.pop(0)
            if quotes_part is not None:
                if arg_s.endswith("'"):
                    arg_s = arg_s[:-1]  # Strip final '
                quotes_part += ' ' + arg_s
                args.append(quotes_part)
                quotes_part = None
            elif arg_s.startswith("'"):
                arg_s = arg_s[1:]  # Strip initial '
                if arg_s.endswith("'"):
                    arg_s = arg_s[:-1]  # Strip final '
                    args.append(arg_s)
                else:
                    quotes_part = arg_s
            else:
                if arg_s.startswith('$'):
                    args.append(self._resolve_entity(arg_s[1:]))
                else:
                    try:
                        args.append(float(arg_s))
                    except ValueError:
                        raise ValueError('Syntax error: %s is not a float. '
                                         'If it is supposed to be a string, '
                                         'enclose it in single quotes.'
                                         % (arg_s,))
        return args

    def _parse_prefix(self, prefix):
        prefix = prefix.strip().split('&')
        if len(prefix) > 2:
            raise ValueError('Syntax error: multiple "&" in prefix')
        conditions = prefix[0].strip().split(',')
        if len(prefix) == 2:
            label = prefix[1].strip()
        else:
            label = None
        if len(conditions) == 0:
            raise ValueError("Syntax error: expected at least one condition")
        elif len(conditions) > 2:
            raise ValueError("Syntax error: expected at most two condition")
        t, trigger = self._parse_conditions(*[x.strip() for x in conditions])
        return label, t, trigger

    def _parse_suffix(self, suffix):
        action_l = suffix.strip().split(' ')
        if action_l[0].startswith('$'):
            entity_id = action_l[0][1:]
            action_l = action_l[1:]
            if len(action_l) == 0:
                raise ValueError('Syntax error: missing action.')
        else:
            entity_id = 'sb'
        entity = self._resolve_entity(entity_id)
        action = self._parse_action(entity, action_l)
        return action

    def _parse_line(self, line):
        parts = line.split('|')
        if len(parts) != 2:
            raise ValueError("Syntax error: expected exactly one '|'")
        label, t, trigger = self._parse_prefix(parts[0])
        action = self._parse_suffix(parts[1])
        event = Event(action, ev_id=label, ev_time=t, trigger=trigger)
        self.add_event(event)

    def parse(self, str_iterable):
        for index, line in enumerate(str_iterable):
            if line.startswith('#'):
                continue
            if line.strip('\n').strip(' ') == '':
                continue
            try:
                self._parse_line(line)
            except ValueError as e:
                raise ValueError(str(e) + ' -> @ line %s' % (index,))

    def write(self, buffer):
        ev_list = list(self.events_by_id.values())
        ev_list.sort(key=lambda x: x.time if x.time is not None else float('+inf'))
        for event in ev_list:
            buffer.write(repr(event) + '\n')

    def _parse_conditions(self, *conditions):
        """
        Parses condition strings and returns the conditions
        @param conditions: list of strings
        @return: (Tuple[float, event]) -> (time, trigger)
        """
        t, trigger = None, None
        for cond in conditions:
            if t is None:
                try:
                    temp = float(cond)
                    if temp > 24 * 3600:  # seconds in a day
                        raise ValueError
                    t = temp
                    continue
                except ValueError:
                    pass
            if trigger is None:
                try:
                    trigger = self.events_by_id[cond]
                    continue
                except KeyError:
                    pass
            raise ValueError('Syntax error: cannot parse condition {}. '
                             'Either the condition is malformed, or there are '
                             'multiple triggers of the same type.')
        return t, trigger
