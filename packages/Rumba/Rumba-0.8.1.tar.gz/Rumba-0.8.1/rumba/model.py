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
import stat

from rumba.elements.topology import (
    DIF,
    ShimEthDIF,
    ShimUDPDIF,
    NormalDIF,

    IPCP,
    ShimEthIPCP,
    ShimUDPIPCP,

    Node,
    SSHConfig,

    LinkQuality,
    Delay,
    Loss,
    Distribution
)

from rumba.elements.experimentation import (
    Experiment,
    Testbed,
    Executor,
    tmp_dir
)


__all__ = [
    # Topology
    "DIF",
    "ShimEthDIF",
    "ShimUDPDIF",
    "NormalDIF",

    "IPCP",
    "ShimEthIPCP",
    "ShimUDPIPCP",

    "Node",
    "SSHConfig",

    "LinkQuality",
    "Delay",
    "Loss",
    "Distribution",

    # Experimentation
    "Experiment",
    "Testbed",
    "Executor",
    "tmp_dir",

    # Other
    "cache_dir"
]


try:
    os.mkdir(tmp_dir)
    os.chmod(tmp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
except OSError:
    # Already there, nothing to do
    pass

cache_parent_dir = os.path.join(os.path.expanduser("~"), '.cache/')
try:
    os.mkdir(cache_parent_dir)
except OSError:
    # Already there, nothing to do
    pass
cache_dir = os.path.join(os.path.expanduser("~"), '.cache/rumba/')
try:
    os.mkdir(cache_dir)
except OSError:
    # Already there, nothing to do
    pass
