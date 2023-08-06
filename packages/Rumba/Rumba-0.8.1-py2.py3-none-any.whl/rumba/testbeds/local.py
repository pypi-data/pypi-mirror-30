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

import rumba.model as mod
import rumba.log as log

from rumba.executors.local import LocalExecutor

logger = log.get_logger(__name__)

class Testbed(mod.Testbed):
    """
    Local testbed, does not do anything. In the case of the Ouroboros
    plugin this is useful since the Ouroboros plugin will simply create
    processes locally. Also useful for debugging in the other plugins.
    """

    def __init__(self, exp_name, username, proj_name="ARCFIRE", password=""):
        """
        Initializes the parent class.

        :param exp_name: The experiment name.
        :param username: User of the experiment.
        :param proj_name: Project name of the experiment.
        :param password: Password of the user.
        """
        mod.Testbed.__init__(self, exp_name, username, password, proj_name)

        self.executor = LocalExecutor(self)

    def _swap_in(self, experiment):
        """
        Does not actually swap the experiment in.

        :param experiment: The experiment object.
        """
        logger.info("Experiment swapped in")

    def _swap_out(self, experiment):
        """
        Does not actually swap the experiment out.

        :param experiment: The experiment object.
        """
        logger.info("Experiment swapped out")
