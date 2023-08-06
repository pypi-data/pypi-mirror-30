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


from enum import Enum

import rumba.log as log

logger = log.get_logger(__name__)


class DIF(object):
    """
    Base class for DIFs.
    """
    def __init__(self, name, members=None):
        """
        :param name: Name of the DIF.
        :param members: List of nodes that are members of the DIF.
        """
        self.name = name
        if members is None:
            members = list()
        self.members = members
        self.ipcps = list()

    def __repr__(self):
        s = "DIF %s" % self.name
        return s

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other is not None and self.name == other.name

    def __neq__(self, other):
        return not self == other

    def add_member(self, node):
        self.members.append(node)

    def del_member(self, node):
        self.members.remove(node)

    def get_ipcp_class(self):
        return IPCP


# Shim over UDP
#
class ShimUDPDIF(DIF):
    """
    Shim over UDP.
    """
    def __init__(self, name, members=None):
        """
        :param name: Name of the DIF.
        :param members: List of members of the DIF.
        """
        DIF.__init__(self, name, members)

    def get_ipcp_class(self):
        return ShimUDPIPCP


# Shim over Ethernet
#
# @link_speed [int] Speed of the Ethernet network, in Mbps
#
class ShimEthDIF(DIF):
    """
    Shim over Ethernet.
    """
    def get_e_id(self):
        return "ShimEthDIF." + self.name

    def __init__(self, name, members=None, link_quality=None):
        """
        :param name: Name of the DIF.
        :param members: List of members of the DIF.
        :param link_quality: Quality of the link.
        """
        DIF.__init__(self, name, members)
        self._link_quality = link_quality if link_quality is not None else LinkQuality()

    def get_ipcp_class(self):
        return ShimEthIPCP

    def add_member(self, node):
        super(ShimEthDIF, self).add_member(node)
        if len(self.members) > 2:
            raise Exception("More than 2 members in %s!" % self.name)

    @property
    def link_quality(self):
        return self._link_quality

    @link_quality.setter
    def link_quality(self, _link_quality):
        if not _link_quality:
            raise ValueError("Cannot set link_quality to None, use del "
                             "link_quality to reset")

        self._link_quality = _link_quality

        _link_quality.apply(self)

    @link_quality.deleter
    def link_quality(self):
        self._link_quality.deactivate(self)

    def set_delay(self, delay=0,
                  jitter=None,
                  correlation=None,
                  distribution=None):
        """
        Set the delay parameters of the underlying link.
        Parameters as in :py:class:`.Delay`

        :param delay: average delay in ms
        :type delay: :py:class:`int`
        :param jitter: jitter in ms
        :type jitter: :py:class:`int`
        :param correlation: correlation in %
        :type correlation: :py:class:`int`
        :param distribution: delay distribution, defaults to a Normal
                             distribution
        :type distribution: :py:class:`.Distribution`
        """
        new_delay = Delay(delay, jitter, correlation, distribution)
        new_quality = LinkQuality.clone(self.link_quality, delay=new_delay)
        self.link_quality = new_quality

    def set_loss(self,
                 loss=0,
                 correlation=None):
        """
        Set the loss parameter of the underlying link.
        Parameters as in :py:class:`.Loss`

        :param loss: loss in percentage
        :type loss: :py:class:`int` or :py:class:`float`
        :param correlation: correlation in percentage
        :type correlation: :py:class:`int` or :py:class:`float`
        """
        new_loss = Loss(loss, correlation)
        new_quality = LinkQuality.clone(self.link_quality, loss=new_loss)
        self.link_quality = new_quality

    def set_rate(self, rate=None):
        """
        Set the rate parameter of the underlying link.

        :param rate: The desired rate in mbps
        :type rate: :py:class:`int`
        """
        new_quality = LinkQuality.clone(self.link_quality, rate=rate)
        self.link_quality = new_quality

    def set_quality(self, delay, loss, rate):
        """
        Configure the basic quality parameters of the
        underlying link.

        :param delay: the link delay, in ms
        :type delay: :py:class:`int`
        :param loss: the link loss, as a percentage
        :type loss: :py:class:`float` or :py:class:`int`
        :param rate: the link rate in mbps
        :type rate: :py:class:`int`
        """
        new_quality = LinkQuality(delay, loss, rate)
        self.link_quality = new_quality


class NormalDIF(DIF):
    """
    Normal DIF.
    """
    def __init__(self, name, members=None, policy=None):
        """
        :param name: The name of the DIF.
        :param members: The list of members.
        :param policy: Policies of the normal DIF.
        """
        DIF.__init__(self, name, members)
        if policy is None:
            policy = Policy(self)
        self.policy = policy

    def add_policy(self, comp, pol, **params):
        """
        Adds a policy to the DIF.

        :param comp: Component name.
        :param pol: Policy name
        :param params: Parameters of the policy.
        """
        self.policy.add_policy(comp, pol, **params)

    def del_policy(self, comp=None, pol=None):
        """
        Deletes a policy from the DIF.

        :param comp: Component name.
        :param pol: Policy name
        """
        self.policy.del_policy(comp, pol)

    def show(self):
        """
        :return: A string representing the policies in the DIF.
        """
        s = DIF.__repr__(self)
        for comp, pol_dict in self.policy.get_policies().items():
            for pol, params in pol_dict.items():
                s += "\n       Component %s has policy %s with params %s" \
                     % (comp, pol, params)
        return s


class Distribution(Enum):
    """
    An enum holding different statistical distributions.

    **Values:**

    `NORMAL = 1`

    `PARETO = 2`

    `PARETONORMAL = 3`
    """
    NORMAL = 1
    PARETO = 2
    PARETONORMAL = 3


class Delay(object):
    """
    A class representing delay of a link.
    """
    def __init__(self, delay=0, jitter=None, correlation=None,
                 distribution=None):
        """
        Configure link delay.

        :param delay: average delay in ms
        :type delay: :py:class:`int`
        :param jitter: jitter in ms
        :type jitter: :py:class:`int`
        :param correlation: correlation in %
        :type correlation: :py:class:`int`
        :param distribution: delay distribution, defaults to a Normal
                             distribution
        :type distribution: :py:class:`.Distribution`
        """

        if delay < 0:
            raise ValueError("Delay needs to be at least 0")

        if jitter and not jitter > 0:
            raise ValueError("Jitter needs to be higher than 0")

        if (not jitter) and correlation:
            raise ValueError("Correlation requires a value for jitter")

        if correlation and (correlation < 0 or correlation > 100):
            raise ValueError("Correlation needs to be between 0 and 100")

        self._delay = delay
        self._jitter = jitter
        self._correlation = correlation
        self._distribution = distribution

    @property
    def delay(self):
        return self._delay

    @property
    def jitter(self):
        return self._jitter

    @property
    def correlation(self):
        return self._correlation

    @property
    def distribution(self):
        return self._distribution

    def build_command(self):
        opts = ["delay %ims" % self.delay]

        if self.jitter:
            opts.append("%ims" % self.jitter)

            if self.correlation:
                opts.append("%f%%" % self.correlation)

        if self.distribution:
            opts.append("distribution %s" % self.distribution.name.lower())

        return " ".join(opts)


class Loss(object):
    """
    A class representing loss on a link.
    """
    def __init__(self, loss, correlation=None):
        """
        Configure link loss.

        :param loss: loss in percentage
        :type loss: :py:class:`int` or :py:class:`float`
        :param correlation: correlation in percentage
        :type correlation: :py:class:`int` or :py:class:`float`
        """
        if loss and (loss < 0 or loss > 100):
            raise ValueError("Loss needs to be between 0 and 100")

        if correlation and (correlation < 0 or correlation > 100):
            raise ValueError("Correlation needs to be between 0 and 100")

        self._loss = loss
        self._correlation = correlation

    @property
    def loss(self):
        return self._loss

    @property
    def correlation(self):
        return self._correlation

    def build_command(self):
        opts = ["loss %f%%" % self.loss]

        if self.correlation:
            opts.append("%f%%" % self.correlation)

        return " ".join(opts)


class LinkQuality(object):
    """
    A class representing the link quality.
    """
    _active = set()

    @classmethod
    def clone(cls, old_quality, delay=None, loss=None, rate=None):
        """
        Clone old_quality, updating it with the provided parameters
        if present.

        :param old_quality: A :py:class:`.LinkQuality` instance to
                            use as a base
        :type old_quality: :py:class:`.LinkQuality`
        :param delay: Delay object holding delay configuration
                      or number corresponding to delay in ms
        :type delay: :py:class:`.Delay` or :py:class:`int`
        :param loss: Loss object holding delay configuration or
                     number corresponding to loss percentage
        :type loss: :py:class:`.Loss` or :py:class:`float`
        :param rate: The rate of the link in mbit
        :type rate: :py:class:`int`
        :return: a new :py:class:`.LinkQuality` instance.
        :rtype: :py:class:`.LinkQuality`
        """
        if delay is None:
            delay = old_quality.delay
        if loss is None:
            loss = old_quality.loss
        if rate is None:
            rate = old_quality.rate
        return LinkQuality(delay, loss, rate)

    def __init__(self, delay=None, loss=None, rate=None):
        """
        Link quality configuration.

        :param delay: Delay object holding delay configuration
                      or number corresponding to delay in ms
        :type delay: :py:class:`.Delay` or :py:class:`int`
        :param loss: Loss object holding delay configuration or
                     number corresponding to loss percentage
        :type loss: :py:class:`.Loss` or :py:class:`float`
        :param rate: The rate of the link in mbit
        :type rate: :py:class:`int`
        """

        if rate and not rate > 0:
            raise ValueError("Rate needs to be higher than 0")

        if isinstance(delay, int):
            delay = Delay(delay)
        if isinstance(loss, int) or isinstance(loss, float):
            loss = Loss(loss)
        self._delay = delay
        self._loss = loss
        self._rate = rate

    @property
    def delay(self):
        return self._delay

    @property
    def loss(self):
        return self._loss

    @property
    def rate(self):
        return self._rate

    def build_command(self, ipcp):
        cmd = []

        if ipcp in LinkQuality._active:
            cmd.append("tc qdisc change dev %s root netem" % ipcp.ifname)
        else:
            cmd.append("tc qdisc add dev %s root netem" % ipcp.ifname)

        if self.delay:
            cmd.append(self.delay.build_command())

        if self.loss:
            cmd.append(self.loss.build_command())

        if self.rate:
            cmd.append("rate %imbit" % self.rate)

        return " ".join(cmd)

    def apply(self, shim):
        if not (self.delay or self.loss or self.rate):
            self.deactivate(shim)
        else:
            for ipcp in shim.ipcps:
                if not ipcp.ifname:
                    logger.error("Could not apply LinkQuality to IPCP because "
                                 "the interface name is None")
                    continue

                ipcp.node.execute_command(self.build_command(ipcp),
                                          as_root=True)
                LinkQuality._active.add(ipcp)

    def deactivate(self, shim):
        for ipcp in shim.ipcps:
            if ipcp not in LinkQuality._active:
                continue
            if not ipcp.ifname:
                logger.error("Could not remove LinkQuality from IPCP because "
                             "the interface name is None")
                continue

            ipcp.node.execute_command("tc qdisc del dev %s root "
                                      "netem" % ipcp.ifname, as_root=True)
            LinkQuality._active.remove(ipcp)


class SSHConfig(object):
    def __init__(self, hostname, port=22, proxy_server=None):
        self.username = None
        self.password = None
        self.hostname = hostname
        self.port = port
        self.proxy_server = proxy_server
        self.client = None
        self.proxy_client = None
        self.http_proxy = None

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def set_http_proxy(self, proxy):
        self.http_proxy = proxy


class Node(object):
    """
    A node in the experiment.
    """
    def get_e_id(self):
        return "Node." + self.name

    def __init__(self, name, difs=None, dif_registrations=None,
                 policies=None, machine_type=None):
        """
        :param name: Name of the node.
        :param difs: A list of DIFs the node is in.
        :param dif_registrations: How the DIFs are stacked.
        :param policies: Policies of a DIF specific to the node.
        :param machine_type: Type of machine to use, physical or virtual.
        """
        self.name = name
        if difs is None:
            difs = list()
        self.difs = difs
        for dif in self.difs:
            dif.add_member(self)
        if dif_registrations is None:
            dif_registrations = dict()
        self.dif_registrations = dif_registrations
        self.machine_type = machine_type
        self.ssh_config = SSHConfig(name)
        self.ipcps = []
        self.policies = dict()
        self.has_tcpdump = False
        if policies is None:
            policies = dict()
        for dif in self.difs:
            if hasattr(dif, 'policy'):  # check if the dif supports policies
                self.policies[dif] = policies.get(dif, Policy(dif, self))

        self.executor = None  # will be set by testbed on swap_in
        self.startup_command = None  # will be set by prototype

        self._validate()

    def get_ipcp_by_dif(self, dif):
        """
        :param dif: The DIF to get the IPCP of.
        :return: The IPCP of the node that is in the DIF.
        """
        for ipcp in self.ipcps:
            if ipcp.dif == dif:
                return ipcp

    def _undeclared_dif(self, dif):
        if dif not in self.difs:
            raise Exception("Invalid registration: node %s is not declared "
                            "to be part of DIF %s" % (self.name, dif.name))

    def _validate(self):
        # Check that DIFs referenced in self.dif_registrations
        # are part of self.difs
        for upper in self.dif_registrations:
            self._undeclared_dif(upper)
            for lower in self.dif_registrations[upper]:
                self._undeclared_dif(lower)

    def __repr__(self):
        s = "Node " + self.name + ":\n"

        s += "  DIFs: [ "
        s += " ".join([d.name for d in self.difs])
        s += " ]\n"

        s += "  DIF registrations: [ "
        rl = []
        for upper in self.dif_registrations:
            difs = self.dif_registrations[upper]
            x = "%s => [" % upper.name
            x += " ".join([lower.name for lower in difs])
            x += "]"
            rl.append(x)
        s += ", ".join(rl)
        s += " ]\n"

        return s

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other is not None and self.name == other.name

    def __neq__(self, other):
        return not self == other

    def add_dif(self, dif):
        """
        Adds a DIF to the list.

        :param dif: Name of the DIF to add.
        """
        self.difs.append(dif)
        dif.add_member(self)
        if hasattr(dif, 'policy'):
            self.policies[dif] = Policy(dif, self)
        self._validate()

    def del_dif(self, dif):
        """
        Adds a DIF to the list.

        :param dif: Name of the DIF to add.
        """
        self.difs.remove(dif)
        dif.del_member(self)
        try:
            del self.policies[dif]
        except KeyError:
            # It was not in there, so nothing to do
            pass
        self._validate()

    def add_dif_registration(self, upper, lower):
        """
        Adds a DIF registration.

        :param upper: Name of the DIF that is requesting IPC.
        :param lower: Name of the DIF providing IPC.
        """
        self.dif_registrations[upper].append(lower)
        self._validate()

    def del_dif_registration(self, upper, lower):
        """
        Removes a DIF registration.

        :param upper: Name of the DIF that is requesting IPC.
        :param lower: Name of the DIF providing IPC.
        """
        self.dif_registrations[upper].remove(lower)
        self._validate()

    def add_policy(self, dif, component_name, policy_name, **parameters):
        """
        Adds a policy.

        :param dif: The name of the DIF.
        :param component_name: Name of the component.
        :param policy_name: Name of the policy.
        :param parameters: Parameters of the policy.
        """
        self.policies[dif].add_policy(component_name, policy_name, **parameters)

    def del_policy(self, dif, component_name=None, policy_name=None):
        """
         Removes a policy.

        :param dif: the dif to which the policy should be applied
        :param component_name: Name of the component.
        :param policy_name: Name of the policy.
        """
        self.policies[dif].del_policy(component_name, policy_name)

    def get_policy(self, dif):
        """
        :param dif: The DIF to get the policy of.
        :return: Returns the policy.
        """
        return self.policies[dif]

    def execute_commands(self, commands, as_root=False, time_out=3,
                         use_proxy=False):
        """
        Execute a list of a commands on the node.

        :param commands: A list of commands.
        :param as_root: Execute as root?
        :param time_out: Seconds before timing out.
        :param use_proxy: Use a proxy to execute the commands?
        """
        return self.executor.execute_commands(self,
                                              commands,
                                              as_root,
                                              time_out)

    def execute_command(self, command, as_root=False, time_out=3,
                        use_proxy=False):
        """
        Execute a single command on a node.

        :param command: A command.
        :param as_root: Execute as root?
        :param time_out: Seconds before timing out.
        :param use_proxy: Use a proxy to execute the commands?
        :return: The stdout of the command.
        """
        return self.executor.execute_command(self,
                                             command,
                                             as_root,
                                             time_out)

    def copy_file(self, path, destination):
        """
        Copy file to node.

        :param path: Local location of the file.
        :param destination: Destination location of the file.
        """
        self.executor.copy_file(self, path, destination)

    def copy_files(self, paths, destination):
        """
        Copy files to node.

        :param paths: Local location of the files.
        :param destination: Destination location of the files.
        """
        self.executor.copy_files(self, paths, destination)

    def fetch_file(self, path, destination, sudo=False):
        """
        Fetch file from the node.

        :param path: Location of the files on the node.
        :param destination: Destination location of the files.
        :param sudo: The file is owned by root on the node?
        """
        self.executor.fetch_file(self, path, destination, sudo)

    def fetch_files(self, paths, destination, sudo=False):
        """
        Fetch files from the node.

        :param paths: Location of the files on the node.
        :param destination: Destination location of the files.
        :param sudo: The file is owned by root on the node?
        """
        self.executor.fetch_files(self, paths, destination, sudo)

    def set_link_state(self, dif, state):
        """
        Change the state of a link on the node.

        :param dif: The name of the shim Ethernet DIF.
        :param state: Up or down.
        """
        ipcp = self.get_ipcp_by_dif(dif)
        self.execute_command('ip link set dev ' + ipcp.ifname + ' ' + state,
                             as_root=True)


class IPCP(object):
    def __init__(self, name, node, dif):
        self.name = name
        self.node = node
        self.dif = dif
        self.registrations = []

        # Is this IPCP the first in its DIF, so that it does not need
        # to enroll to anyone ?
        self.dif_bootstrapper = False

    def __repr__(self):
        return "{IPCP=%s,DIF=%s,N-1-DIFs=(%s)%s}" % \
                (self.name, self.dif.name,
                 ' '.join([dif.name for dif in self.registrations]),
                 ',bootstrapper' if self.dif_bootstrapper else ''
                 )

    def __hash__(self):
        return hash((self.name, self.dif.name))

    def __eq__(self, other):
        return other is not None and self.name == other.name \
                                and self.dif == other.dif

    def __neq__(self, other):
        return not self == other


class ShimEthIPCP(IPCP):
    def __init__(self, name, node, dif, ifname=None):
        IPCP.__init__(self, name, node, dif)
        self.ifname = ifname


class ShimUDPIPCP(IPCP):
    def __init__(self, name, node, dif):
        IPCP.__init__(self, name, node, dif)
        # TODO: add IP and port


class Policy(object):
    def __init__(self, dif, node=None, policies=None):
        self.dif = dif  # type: NormalDIF
        self.node = node
        if policies is None:
            self._dict = dict()
        else:
            self._dict = policies

    def add_policy(self, component_name, policy_name, **parameters):
        self._dict.setdefault(component_name, dict())[policy_name] = parameters

    #
    # Fetches effective policy info
    #
    def get_policies(self, component_name=None, policy_name=None):
        policy = self._superimpose()
        if component_name is None:
            return policy._dict
        elif policy_name is None:
            return policy._dict[component_name]
        else:
            return policy._dict[component_name][policy_name]

    def del_policy(self, component_name=None, policy_name=None):
        if component_name is None:
            self._dict = dict()
        elif policy_name is None:
            del self._dict[component_name]
        else:
            del self._dict[component_name][policy_name]

    #
    # Merges this policy into that of its dif, obtaining
    # the effective policy acting on self.node.
    #
    def _superimpose(self):
        if self.node is None:
            return self
        other = self.dif.policy
        base = dict(other._dict)
        base.update(self._dict)
        return Policy(self.dif, self.node, base)

    def __eq__(self, other):
        if not isinstance(other, Policy):
            return False
        else:
            return other.dif == self.dif \
                   and other.node == self.node \
                   and other._dict == self._dict

    def __str__(self):
        node_str = (" Node: " + self.node) if self.node is not None else ""
        return "Policy[Dif: %(dif)s,%(node_str)s Dict: %(dict)s]" \
               % {"dif": self.dif, "node_str": node_str, "dict": self._dict}

    def __repr__(self):
        node_str = (" Node: " + self.node) if self.node is not None else ""
        s = "Policy[ Dif: %(dif)s,%(node_str)s" \
            % {"dif": self.dif, "node_str": node_str}
        comps = []
        for component in self._dict:
            for policy in self._dict[component]:
                comps.append("\n  Component %s has policy %s with params %s"
                             % (component,
                                policy,
                                self._dict[component][policy]))
        s += ",".join(comps)
        s += "\n]\n"
        return s
