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

import sys
from setuptools import setup

is_windows = sys.platform == 'win32'

datafiles = (
        ('/usr/sbin', ('bin/virid', 'bin/virid-conf')),
        ('/usr/bin', ('bin/viric',)),
        ('/etc/viri', ('conf/virid.conf',)),
    ) if not is_windows else ()

kwargs = dict(name='viri',
    version='0.1',
    description='Remote execution of Python scripts',
    author='Marc Garcia',
    author_email='garcia.marc@gmail.com',
    url='http://www.viriproject.com',
    packages=('libviri',),
    data_files=datafiles,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: System :: Systems Administration',
    )
)

setup(**kwargs)

