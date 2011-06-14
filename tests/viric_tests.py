# rpcserver.py tests

r"""
>>> import os
>>> import shutil

# Copying viric file to this directory to be able to import it
>>> shutil.copyfile(os.path.join('..', 'bin', 'viric'), 'viric.py')
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

