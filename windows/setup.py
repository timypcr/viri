#!/usr/bin/env python3

# Copyright 2011, Marc Garcia <garcia.marc@gmail.com>
#
# This file is part of Viri.
#
# Viri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Viri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Viri.  If not, see <http://www.gnu.org/licenses/>.

import imp
from os.path import dirname, abspath, join
from cx_Freeze import setup, Executable

MOD_NAME = 'setup'

file_obj, path, desc = imp.find_module(MOD_NAME, [
    join(dirname(dirname(abspath(__file__))), 'virid')
])
mod = imp.load_module(MOD_NAME, file_obj, path, desc)

kwargs = mod.kwargs

kwargs.update(dict(
    executables = [Executable('bin/virid')],
))

setup(**kwargs)

