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

r"""
>>> import os
>>> import shutil

# Copying viric file to this directory to be able to import it
>>> shutil.copyfile(os.path.join('..', 'client', 'viric'), 'viric.py')
>>> import viric

>>> viric._fix_file_params('ls', {})
{}
>>> viric._fix_file_params('execute', {'use_id': True, 'file_or_id': '1234'}).get('script_id', 'NOT_FOUND')
'1234'
>>> viric._fix_file_params('execute', {'use_id': True, 'file_or_id': '1234'}).get('file_or_id', 'NOT_FOUND')
'NOT_FOUND'
>>> viric._fix_file_params('execute', {'use_id': False, 'file_or_id': '__init__.py'}).get('script_id', 'NOT_FOUND')
'NOT_FOUND'
>>> viric._fix_file_params('execute', {'use_id': False, 'file_or_id': '__init__.py'}).get('file_name', 'NOT_FOUND')
'__init__.py'
>>> viric._fix_file_params('execute', {'use_id': False, 'file_or_id': '__init__.py'}).get('file_or_id', 'NOT_FOUND')
'NOT_FOUND'



>>> os.remove('viric.py')

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

