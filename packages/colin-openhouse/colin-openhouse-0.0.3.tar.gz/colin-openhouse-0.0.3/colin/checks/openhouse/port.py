# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re

from colin.checks.abstract.containers import ContainerCheck
from colin.checks.abstract.images import ImageCheck
from colin.checks.result import CheckResult


class __WorkDirCheck(ContainerCheck, ImageCheck):

    def __init__(self):
        super().__init__(name="port80",
                         message="Expose the port 80.",
                         description="Use EXPOSE 12345 to inform docker about port of your service."
                                     "Použij EXPOSE 12345 pro informování dockeru o portu služby.",
                         reference_url="https://fedoraproject.org/wiki/Container:Guidelines#expose",
                         tags=["workdir", "required"])

        self.port = {"80/tcp": {}}

    def check(self, target):
        if not "ExposedPorts" in target.instance.get_metadata()["Config"]:
            passed = False
        else:
            port = target.instance.get_metadata()["Config"]["ExposedPorts"]
            passed = port is not None and self.port == port

        return CheckResult(ok=passed,
                           severity=self.severity,
                           description=self.description,
                           message=self.message,
                           reference_url=self.reference_url,
                           check_name=self.name,
                           logs=[])
