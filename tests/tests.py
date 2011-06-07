"""Script for executing viri tests.

Usage:
    tests.py [modules_to_test]

    modules_to_test: Optional list of test modules to execute, if not provided,
        all test modules are tested

Example usage:
    tests.py -- Executes all tests
    tests.py schedserver -- Executes schedserver.py tests
    tests.py schedserver rpcserver -- Executes schedserver.py and rpcserver.py
        tests
"""
import sys
import os
import doctest

ALL_TESTS = ('rpcserver', 'schedserver')

def set_path():
    parent_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    sys.path.append(os.path.join(parent_dir, 'viri'))

def exec_tests(tests):
    for test in tests:
        test_mod = __import__('%s_tests' % test, globals(), locals())
        doctest.testmod(test_mod)

if __name__ == '__main__':
    set_path()
    if len(sys.argv) == 1:
        exec_tests(ALL_TESTS)
    else:
        exec_tests(sys.argv[1:])

