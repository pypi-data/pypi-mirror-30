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

from rumba import model as mod

import subprocess

from rumba import log

logger = log.get_logger(__name__)


class LocalExecutor(mod.Executor):
    def __init__(self, testbed):
        self.testbed = testbed

    def execute_command(self, node, cmd, sudo=False, time_out=3):
        try:
            logger.debug("%s >> %s" % (node.name, cmd))
            subprocess.check_call(cmd.split(' '))
        except subprocess.CalledProcessError as e:
            logger.error("Return code was " + str(e.returncode))
            raise

    def fetch_file(self, node, path, destination, as_root=False):
        logger.error("Fetch_file not supported for local testbed")
        raise

    def copy_file(self, node, path, destination):
        logger.error("Copy_file not supported for local testbed")
        raise
