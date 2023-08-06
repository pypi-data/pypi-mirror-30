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

import tempfile
import tarfile

from rumba import log

logger = log.get_logger(__name__)


class DockerException(Exception):
    pass


class DockerExecutor(mod.Executor):
    def __init__(self, testbed):
        self.testbed = testbed
        self.running_containers = testbed.running_containers

    def execute_command(self, node, command, sudo=False, time_out=3):
        logger.debug("%s >> %s" % (node.name, command))

        c, o = self.running_containers[node.name].exec_run(["sh", "-c",
                                                            command])
        if c:
            raise DockerException('A remote command returned an error. '
                                  'Output:\n\n\t' + o.decode("utf-8"))

        return o.decode("utf-8")

    def fetch_file(self, node, path, destination, as_root=False):
        if not path.startswith("/"):
            workingdir = self.running_containers[node.name].attrs["Config"][
                "WorkingDir"]
            path = os.path.join(workingdir, path)

        try:
            with tempfile.NamedTemporaryFile() as tmp:
                archive, _ = self.running_containers[node.name].get_archive(
                    path)

                for c in archive:
                    tmp.write(c)

                tmp.seek(0)

                tarfile.TarFile(fileobj=tmp, mode='r').extract(
                    path.basename(path), destination)
        except:
            logger.error("Error when extracting %s" % path)

    def copy_file(self, node, path, destination):
        pass
