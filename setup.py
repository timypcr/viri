from setuptools import setup

setup(name='viri',
    version='0.0.1',
    description='Remote execution of Python scripts',
    author='Marc Garcia',
    author_email='garcia.marc@gmail.com',
    url='http://www.viriproject.com',
    data_files=(
        ('/etc/viri', ('etc/viri/virid.conf',)),
        ('/etc/init.d', ('etc/init.d/virid',)),
    ),
    scripts=('bin/virid', 'bin/viric'),
    packages=('viri',),
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

