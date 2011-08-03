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
>>> import logging
>>> import xmlrpc.client
>>> from viri import orm, objects, rpcserver

>>> logging.disable(logging.CRITICAL)

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
...     for line in response:
...         del line[date_col] # remove date
...         result.append(','.join(['{}={}'.format(x, y) for x, y in line.items()]))
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
(True, '0fdeee3bf255a30a207a3c84934defb9eb00efb0')
>>> rpcs.put({'file_name': 'data_file_2.txt',
...     'file_content': xmlrpc.client.Binary(b'file 2 content\n')})
(True, '19c32940f2e5f997bc34530cf9b544247e674168')

# List and get data files
>>> print(format_response(rpcs.ls({})[1], 'saved'))
file_name=data_file_1,file_id=0fdeee3bf255a30a207a3c84934defb9eb00efb0
file_name=data_file_2.txt,file_id=19c32940f2e5f997bc34530cf9b544247e674168
>>> rpcs.get({'file_name_or_id': 'data_file_1'})[1].data
b'file 1 content\n'
>>> rpcs.get({'file_name_or_id': '0fdeee3bf255a30a207a3c84934defb9eb00efb0'})[1].data
b'file 1 content\n'
>>> rpcs.get({'file_name_or_id': 'data_file_2.txt'})[1].data
b'file 2 content\n'
>>> rpcs.get({'file_name_or_id': '19c32940f2e5f997bc34530cf9b544247e674168'})[1].data
b'file 2 content\n'
>>> rpcs.get({'file_name_or_id': 'not_sent_data_file'})
(False, 'File not found')

# Put scripts
>>> rpcs.put({'file_name': 'syntax_error.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_SYNTAX_ERROR)})
(True, 'f8b8b3454691870fa1bbd323698802ee29155cb6')
>>> rpcs.put({'file_name': 'no_class.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_NO_CLASS)})
(True, '8d216cb3d41bca080407eebb96384f941d4da793')
>>> rpcs.put({'file_name': 'no_run.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_NO_RUN)})
(True, '4a1f32f97b8691985630251c9f53654483aeca61')
>>> rpcs.put({'file_name': 'correct.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_CORRECT)})
(True, '6bd4e019d841ea7716ec0cd3be86b878edca47ab')
>>> rpcs.put({'file_name': 'with_arg.py',
...     'file_content': xmlrpc.client.Binary(SCRIPT_WITH_ARG)})
(True, '0532ddf128bb22cee16ad6ea7c933fc4106fab9b')

# List and get scripts
>>> print(format_response(rpcs.ls({})[1], 'saved'))
file_name=correct.py,file_id=6bd4e019d841ea7716ec0cd3be86b878edca47ab
file_name=data_file_1,file_id=0fdeee3bf255a30a207a3c84934defb9eb00efb0
file_name=data_file_2.txt,file_id=19c32940f2e5f997bc34530cf9b544247e674168
file_name=no_class.py,file_id=8d216cb3d41bca080407eebb96384f941d4da793
file_name=no_run.py,file_id=4a1f32f97b8691985630251c9f53654483aeca61
file_name=syntax_error.py,file_id=f8b8b3454691870fa1bbd323698802ee29155cb6
file_name=with_arg.py,file_id=0532ddf128bb22cee16ad6ea7c933fc4106fab9b


# Script execution
>>> rpcs.execute({'file_name_or_id': 'not_sent_script', 'args': ''})
(False, 'File not found')
>>> rpcs.execute({'file_name_or_id': 'not_sent_script.py', 'args': ''})
(False, 'File not found')
>>> rpcs.execute({'file_name_or_id': 'syntax_error.py', 'args': ''})
(False, 'Traceback (most recent call last):\n  File "syntax_error.py", line 2\n    print(\'syntax error\n                      ^\nSyntaxError: EOL while scanning string literal\n')
>>> rpcs.execute({'file_name_or_id': 'f8b8b3454691870fa1bbd323698802ee29155cb6', 'args': ''})
(False, 'Traceback (most recent call last):\n  File "syntax_error.py", line 2\n    print(\'syntax error\n                      ^\nSyntaxError: EOL while scanning string literal\n')
>>> rpcs.execute({'file_name_or_id': 'no_class.py', 'args': ''})
(False, 'Script does not have a ViriScript class')
>>> rpcs.execute({'file_name_or_id': '8d216cb3d41bca080407eebb96384f941d4da793', 'args': ''})
(False, 'Script does not have a ViriScript class')
>>> rpcs.execute({'file_name_or_id': 'no_run.py', 'args': ''})
(False, 'ViriScript class does not have a run method')
>>> rpcs.execute({'file_name_or_id': '4a1f32f97b8691985630251c9f53654483aeca61', 'args': ''})
(False, 'ViriScript class does not have a run method')
>>> rpcs.execute({'file_name_or_id': 'correct.py', 'args': ''})
(True, 'Hello world!')
>>> rpcs.execute({'file_name_or_id': '6bd4e019d841ea7716ec0cd3be86b878edca47ab', 'args': ''})
(True, 'Hello world!')
>>> rpcs.execute({'file_name_or_id': 'with_arg.py', 'args': ('Foo',)})
(True, 'Hello Foo!')

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

