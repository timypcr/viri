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

>>> SCRIPT_WITH_ARG = b'''
... class ViriScript:
...     def run(self, name):
...         return 'Hello {}!'.format(name)
... '''

>>> def format_response(response, date_col):
...     result = []
...     for line in response.split('\n'):
...         line_arr = line.split('\t')
...         line_arr.pop(date_col) # remove date
...         result.append(' '.join(line_arr))
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
>>> print(format_response(rpcs.ls({})[1], 2))
data_file_1 0fdeee3bf255a30a207a3c84934defb9eb00efb0
data_file_2.txt 19c32940f2e5f997bc34530cf9b544247e674168
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
>>> rpcs.put({'file_name': 'correct.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_CORRECT)})
(0, '6bd4e019d841ea7716ec0cd3be86b878edca47ab')
>>> rpcs.put({'file_name': 'with_arg.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_WITH_ARG)})
(0, '0532ddf128bb22cee16ad6ea7c933fc4106fab9b')

# List and get scripts
>>> print(format_response(rpcs.ls({})[1], 2))
correct.py 6bd4e019d841ea7716ec0cd3be86b878edca47ab
data_file_1 0fdeee3bf255a30a207a3c84934defb9eb00efb0
data_file_2.txt 19c32940f2e5f997bc34530cf9b544247e674168
no_class.py 8d216cb3d41bca080407eebb96384f941d4da793
no_run.py 4a1f32f97b8691985630251c9f53654483aeca61
syntax_error.py f8b8b3454691870fa1bbd323698802ee29155cb6
with_arg.py 0532ddf128bb22cee16ad6ea7c933fc4106fab9b

# Script execution
>>> rpcs.history({})
(0, '')
>>> rpcs.execute({'file_name_or_id': 'not_sent_script', 'args': ''})
(1, 'File not found')
>>> rpcs.execute({'file_name_or_id': 'not_sent_script.py', 'args': ''})
(1, 'File not found')
>>> rpcs.execute({'file_name_or_id': 'syntax_error.py', 'args': ''})
(1, 'Traceback (most recent call last):\n  File "syntax_error.py", line 2\n    print(\'syntax error\n                      ^\nSyntaxError: EOL while scanning string literal\n')
>>> rpcs.execute({'file_name_or_id': 'f8b8b3454691870fa1bbd323698802ee29155cb6', 'args': ''})
(1, 'Traceback (most recent call last):\n  File "syntax_error.py", line 2\n    print(\'syntax error\n                      ^\nSyntaxError: EOL while scanning string literal\n')
>>> rpcs.execute({'file_name_or_id': 'no_class.py', 'args': ''})
(1, 'Script does not have a ViriScript class')
>>> rpcs.execute({'file_name_or_id': '8d216cb3d41bca080407eebb96384f941d4da793', 'args': ''})
(1, 'Script does not have a ViriScript class')
>>> rpcs.execute({'file_name_or_id': 'no_run.py', 'args': ''})
(1, 'ViriScript class does not have a run method')
>>> rpcs.execute({'file_name_or_id': '4a1f32f97b8691985630251c9f53654483aeca61', 'args': ''})
(1, 'ViriScript class does not have a run method')
>>> rpcs.execute({'file_name_or_id': 'correct.py', 'args': ''})
(0, 'Hello world!')
>>> rpcs.execute({'file_name_or_id': '6bd4e019d841ea7716ec0cd3be86b878edca47ab', 'args': ''})
(0, 'Hello world!')
>>> rpcs.execute({'file_name_or_id': 'with_arg.py', 'args': ('Foo',)})
(0, 'Hello Foo!')
>>> print(format_response(rpcs.history({})[1], 0))
correct.py 6bd4e019d841ea7716ec0cd3be86b878edca47ab 1
correct.py 6bd4e019d841ea7716ec0cd3be86b878edca47ab 1
no_class.py 8d216cb3d41bca080407eebb96384f941d4da793 0
no_class.py 8d216cb3d41bca080407eebb96384f941d4da793 0
no_run.py 4a1f32f97b8691985630251c9f53654483aeca61 0
no_run.py 4a1f32f97b8691985630251c9f53654483aeca61 0
syntax_error.py f8b8b3454691870fa1bbd323698802ee29155cb6 0
syntax_error.py f8b8b3454691870fa1bbd323698802ee29155cb6 0
with_arg.py 0532ddf128bb22cee16ad6ea7c933fc4106fab9b 1

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

