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
        super().__init__(name="cmd_entrypoint",
                         message='You should set /usr/sbin/httpd as an ENTRYPOINT and set '
                                 'CMD to ["-D", "FOREGROUND"] to run in it in the foreground.',
                         description="Use `ENTRYPOINT` for startup command and CMD for specifying its parameters."
                                     "Použij ENTRYPOINT pro zadání příkazu spouštěného při startu kontejneru "
                                     "a CMD pro zadání jeho parametrů.",
                         reference_url="https://fedoraproject.org/wiki/Container:Guidelines#workdir",
                         tags=["workdir", "required"])

        self.cmd = ["-D", "FOREGROUND"]
        self.entrypoint = ["/usr/sbin/httpd"]

    def check(self, target):
        cmd = target.instance.get_metadata()["Config"]["Cmd"]
        passed = cmd == self.cmd

        entrypoint = target.instance.get_metadata()["Config"]["Entrypoint"]
        passed = passed and (entrypoint == self.entrypoint)

        return CheckResult(ok=passed,
                           severity=self.severity,
                           description=self.description,
                           message=self.message,
                           reference_url=self.reference_url,
                           check_name=self.name,
                           logs=[])
