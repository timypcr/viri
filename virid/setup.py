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
from setuptools.command.install import install

class xinstall(install):
    def run(self):
        install.run(self)
        sys.stdout.write('Host code: ')
        hostcode = input()
        with open('/etc/viri/virid.conf', 'a') as f:
            f.write('\nHostCode: %s\n\n' % hostcode)

setup(name='viri',
    cmdclass={'install': xinstall},
    version='0.1',
    description='Remote execution of Python scripts',
    author='Marc Garcia',
    author_email='garcia.marc@gmail.com',
    url='http://www.viriproject.com',
    packages=('viri',),
    data_files=(
        ('/usr/local/bin', ('bin/viric',)),
        ('/usr/local/sbin', ('bin/virid',)),
        ('/etc/viri', ('conf/virid.conf',)),
        ('/etc/init.d', ('init-script/virid',)),
    ),
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
        'Programming Language :: Python :: 3.1',
        'Topic :: System :: Systems Administration',
    )
)

