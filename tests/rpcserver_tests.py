# rpcserver.py tests

r"""
>>> import shutil
>>> import tempfile
>>> import xmlrpc.client
>>> from viri import scriptmanager
>>> from viri import rpcserver

# Dummy initialization of the server because we are going to access the
# methods directly, and not using the XML-RPC server. We are only
# interested on providing known values for directories
>>> script_dir = tempfile.mkdtemp(prefix='viri-tests-scripts-')
>>> data_dir = tempfile.mkdtemp(prefix='viri-tests-data-')
>>> info_dir = tempfile.mkdtemp(prefix='viri-tests-info-')
>>> context = {}
>>> script_manager = scriptmanager.ScriptManager(
...     script_dir, info_dir, context)
>>> rpcs = rpcserver.RPCServer(6808, '', '', script_dir, data_dir,
...     script_manager)

#################################
### put and get of data files ###
#################################

>>> rpcs.put({'file_name': 'filename1',
...     'file_content': xmlrpc.client.Binary(b'filaname1 content\n'),
...     'data': True})
(0, 'Data file filename1 saved')
>>> rpcs.put({'file_name': 'filename2.txt',
...     'file_content': xmlrpc.client.Binary(b'filaname2 content\n'),
...     'data': True})
(0, 'Data file filename2.txt saved')
>>> rpcs.put({'file_name': 'filename3.py',
...     'file_content': xmlrpc.client.Binary(b'print("hello world!")\n'),
...     'data': True})
(0, 'Data file filename3.py saved')
>>> rpcs.get({'filename_or_id': 'filename1', 'data': True})[1].data
b'filaname1 content\n'
>>> rpcs.put({'file_name': 'filename1',
...     'file_content': xmlrpc.client.Binary(b'filaname1 content modified\n'),
...     'data': True})
(0, 'Not overwriting file filename1')
>>> rpcs.get({'filename_or_id': 'filename1', 'data': True})[1].data
b'filaname1 content\n'
>>> rpcs.put({'file_name': 'filename1',
...     'file_content': xmlrpc.client.Binary(b'filaname1 content modified\n'),
...     'data': True, 'overwrite': True})
(0, 'Data file filename1 overwrote')
>>> rpcs.get({'filename_or_id': 'filename1', 'data': True})[1].data
b'filaname1 content modified\n'
>>> ls_res = rpcs.ls({'data': True})[1].split('\n')
>>> ls_res.sort()
>>> ls_res
['filename1', 'filename2.txt', 'filename3.py']

##################################
### operations with data files ###
##################################

>>> rpcs.mv({'source': 'filename1', 'destination': 'filename4'})
(0, 'File filename1 successfully renamed to filename4')
>>> rpcs.mv({'source': 'filename1', 'destination': 'filename4'})
(1, 'File filename1 not found')
>>> rpcs.mv({'source': 'filename4', 'destination': 'filename2.txt'})
(1, 'Rename aborted because destination file already exists. Use --overwrite to force it')
>>> rpcs.mv({'source': 'filename4', 'destination': 'filename2.txt', 'overwrite': True})
(0, 'Existing file filename2.txt replaced by renaming filename4')
>>> rpcs.rm({'filename': 'filename2.txt'})
(0, 'File filename2.txt successfully removed')
>>> rpcs.rm({'filename': 'filename2.txt'})
(1, 'File not found. File names cannot include directories')
>>> ls_res = rpcs.ls({'data': True})[1].split('\n')
>>> ls_res.sort()
>>> ls_res
['filename3.py']

##############################
### put and get of scripts ###
##############################

>>> rpcs.get({'filename_or_id': 'script1.py',})
(1, 'File not found. File names cannot include directories')
>>> rpcs.put({'file_name': 'script1.py',
...     'file_content': xmlrpc.client.Binary(b'print("hello world!")\n')})
(0, '5db8eb03071c8c231a8f51b3d2a98bd1eb589634')
>>> rpcs.get({'filename_or_id': 'script1.py',})[1].data
b'print("hello world!")\n'
>>> rpcs.put({'file_name': 'script1.py',
...     'file_content': xmlrpc.client.Binary(b'print("hello viri!")\n')})
(0, 'e93c885fc9865db7369d9b516e839a789e8a1622')

##########################
### script definitions ###
##########################

>>> BASE_CORRECT = '''
class ViriScript:
    base_attr = True
'''
>>> SCRIPT_CORRECT = '''
class ViriScript:
    def run(self):
        return '__base__ used: %s ' % hasattr(self, 'base_attr')
'''
>>> SCRIPT_NO_CLASS = '''
base_attr = True
'''
>>> SCRIPT_SYNTAX_ERROR = '''
print('syntax error
'''

####################################
### script execution and history ###
####################################

>>> rpcs.history({})
(0, '')
>>> rpcs.execute({'script_id': 'e93c885fc9865db7369d9b516e839a789e8a1622', 'use_id': True})
(1, '')

################
### clean up ###
################

>>> shutil.rmtree(script_dir)
>>> shutil.rmtree(data_dir)
>>> shutil.rmtree(info_dir)

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

