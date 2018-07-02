# -*- coding: utf-8 -*-
"""Define the Gitcoin pipeline compilers.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from __future__ import unicode_literals

from pipeline.compilers import SubProcessCompiler
from pipeline.conf import settings


class ES6Compiler(SubProcessCompiler):
    """Define the ES6 compiler."""

    output_extension = 'js'

    def match_file(self, path):
        """Define the file path to match."""
        return path.endswith('.js')

    def compile_file(self, infile, outfile, outdated=False, force=False):
        """Transpile the input file from ES6."""
        if not outdated and not force:
            return  # File doesn't need to be recompiled

        command = (settings.BABEL_BINARY, settings.BABEL_ARGUMENTS, infile, '-o', outfile)
        return self.execute_command(command)
