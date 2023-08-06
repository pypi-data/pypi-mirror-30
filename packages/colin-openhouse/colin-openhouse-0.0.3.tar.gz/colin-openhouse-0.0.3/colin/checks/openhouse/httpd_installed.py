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

from colin.checks.abstract.filesystem import FileSystemCheck


class FileCopy(FileSystemCheck):

    def __init__(self):
        super().__init__(name="httpd_installed",
                         message="Package httpd has to be isntalled (dnf install -y httpd).",
                         description="Use RUN for running a command inside an image. Použij RUN pro spuštění příkazu v obraze.",
                         reference_url="https://docs.docker.com/engine/reference/builder/#copy",
                         files=['/usr/sbin/httpd'],
                         tags=['filesystem', 'copy', 'openhouse'],
                         all_must_be_present=False)
