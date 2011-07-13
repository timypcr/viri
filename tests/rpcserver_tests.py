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
>>> import tempfile
>>> import shutil
>>> import xmlrpc.client
>>> from viri import orm, objects, rpcserver

>>> SCRIPT_SYNTAX_ERROR = b'''
... print('syntax error
... '''

>>> SCRIPT_NO_CLASS = b'''
... base_attr = True
... '''

>>> SCRIPT_NO_RUN = b'''
... class ViriScript:
...     base_attr = True
... '''

>>> SCRIPT_CORRECT = b'''
... class ViriScript:
...     def run(self):
...         return 'Hello world!'
... '''

>>> def parse_ls(file_list):
...     result = []
...     for line in file_list.split('\n'):
...         line_arr = line.split('\t')
...         line_arr.pop() # remove saved date
...         result.append('\t'.join(line_arr))
...     result.sort()
...     return '\n'.join(result)

>>> db_file = tempfile.NamedTemporaryFile(prefix='viri_db_')
>>> db = orm.Database(db_file.name)
>>> context = dict(conf={}, db=db)
>>> for obj in objects.objects:
...     obj.create_table(db)
...     context[obj.__name__] = obj

>>> rpcs = rpcserver.RPCServer(
...     port=6808,
...     ca_file=os.path.join('keys', 'ca.cert'),
...     cert_key_file=os.path.join('keys', 'virid.pem'),
...     db=db,
...     context=context)


# Put data files
>>> rpcs.put({'file_name': 'data_file_1',
...     'file_content': xmlrpc.client.Binary(b'file 1 content\n')})
(0, '0fdeee3bf255a30a207a3c84934defb9eb00efb0')
>>> rpcs.put({'file_name': 'data_file_2.txt',
...     'file_content': xmlrpc.client.Binary(b'file 2 content\n')})
(0, '19c32940f2e5f997bc34530cf9b544247e674168')

# List and get data files
>>> parse_ls(rpcs.ls({})[1])
'data_file_1\t0fdeee3bf255a30a207a3c84934defb9eb00efb0\ndata_file_2.txt\t19c32940f2e5f997bc34530cf9b544247e674168'
>>> rpcs.get({'file_name_or_id': 'data_file_1'})[1].data
b'file 1 content\n'
>>> rpcs.get({'file_name_or_id': '0fdeee3bf255a30a207a3c84934defb9eb00efb0'})[1].data
b'file 1 content\n'
>>> rpcs.get({'file_name_or_id': 'data_file_2.txt'})[1].data
b'file 2 content\n'
>>> rpcs.get({'file_name_or_id': '19c32940f2e5f997bc34530cf9b544247e674168'})[1].data
b'file 2 content\n'
>>> rpcs.get({'file_name_or_id': 'not_sent_data_file'})
(1, 'File not found')

# Put scripts
>>> rpcs.put({'file_name': 'syntax_error.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_SYNTAX_ERROR)})
(0, 'f8b8b3454691870fa1bbd323698802ee29155cb6')
>>> rpcs.put({'file_name': 'no_class.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_NO_CLASS)})
(0, '8d216cb3d41bca080407eebb96384f941d4da793')
>>> rpcs.put({'file_name': 'no_run.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_NO_RUN)})
(0, '4a1f32f97b8691985630251c9f53654483aeca61')
>>> rpcs.put({'file_name': 'no_run.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_CORRECT)})
(0, '6bd4e019d841ea7716ec0cd3be86b878edca47ab')

# List and get scripts
>>> parse_ls(rpcs.ls({})[1])
'data_file_1\t0fdeee3bf255a30a207a3c84934defb9eb00efb0\ndata_file_2.txt\t19c32940f2e5f997bc34530cf9b544247e674168\nno_class.py\t8d216cb3d41bca080407eebb96384f941d4da793\nno_run.py\t4a1f32f97b8691985630251c9f53654483aeca61\nno_run.py\t6bd4e019d841ea7716ec0cd3be86b878edca47ab\nsyntax_error.py\tf8b8b3454691870fa1bbd323698802ee29155cb6'

# Script execution
>>> rpcs.history({})
(0, '')
>>> rpcs.execute({'file_name_or_id': 'not_sent_script', 'args': ''})
(1, 'File not found')
>>> rpcs.execute({'file_name_or_id': 'not_sent_script.py', 'args': ''})
(1, 'File not found')
>>> rpcs.execute({'file_name_or_id': 'syntax_error.py', 'args': ''})
(1, 'Traceback (most recent call last):\n  File "syntax_error.py", line 2\n    print(\'syntax error\n                      ^\nSyntaxError: EOL while scanning string literal\n')

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

