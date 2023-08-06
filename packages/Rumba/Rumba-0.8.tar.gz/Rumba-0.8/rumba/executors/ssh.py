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

from rumba.model import Executor
from rumba.ssh_support import execute_command, execute_commands, \
    copy_file_to_testbed, copy_file_from_testbed, execute_proxy_command, \
    execute_proxy_commands


class SSHExecutor(Executor):
    def __init__(self, testbed, use_proxy=False):
        self.testbed = testbed
        self.use_proxy = use_proxy

    def execute_command(self, node, command, as_root=False, time_out=3):
        if as_root:
            if node.ssh_config.username != 'root':
                command = "sudo %s" % command

        if self.use_proxy:
            return execute_proxy_command(self, node.ssh_config, command,
                                         time_out)
        else:
            return execute_command(self.testbed, node.ssh_config, command,
                                   time_out)

    def execute_commands(self, node, commands, as_root=False, time_out=3):
        if self.use_proxy:
            return execute_proxy_commands(self, node.ssh_config, commands,
                                          time_out)
        else:
            return execute_commands(self.testbed, node.ssh_config, commands,
                                    time_out)

    def fetch_file(self, node, path, destination, sudo):
        copy_file_from_testbed(self.testbed, node.ssh_config, path,
                               destination, sudo)

    def copy_file(self, node, path, destination):
        copy_file_to_testbed(self.testbed, node.ssh_config, path, destination)