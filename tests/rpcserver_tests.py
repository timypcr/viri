# rpcserver.py tests

r"""
>>> import shutil
>>> import tempfile
>>> import xmlrpc.client
>>> import scriptmanager
>>> import rpcserver

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

##############################
### put and get of scripts ###
##############################

>>> rpcs.put({'file_name': 'script1.py',
...     'file_content': xmlrpc.client.Binary(b'print("hello world!")\n')})
(0, '5db8eb03071c8c231a8f51b3d2a98bd1eb589634')
>>> rpcs.get({'filename_or_id': 'script1.py',})
b'print("hello world!")\n'
>>> rpcs.put({'file_name': 'script1.py',
...     'file_content': xmlrpc.client.Binary(b'print("hello viri!")\n')})
(0, 'e93c885fc9865db7369d9b516e839a789e8a1622')

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

