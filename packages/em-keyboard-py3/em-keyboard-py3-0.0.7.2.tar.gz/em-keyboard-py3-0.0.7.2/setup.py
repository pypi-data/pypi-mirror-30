#!/usr/bin/env python

import os
import re
import sys
from codecs import open

from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py register')
    os.system('python setup.py sdist upload')
    # os.system('python setup.py bdist_wheel upload --universal')
    sys.exit()

requires = ['docopt', 'xerox']
version = '0.0.7.2'

def read(f):
    return open(f, encoding='utf-8').read()

setup(
    name='em-keyboard-py3',
    version=version,
    description='The CLI Emoji Keyboard',
    long_description=read('README.rst'),
    author='Christian Sauer',
    author_email='sauerc@gmail.com',
    url='https://github.com/c17r/em-keyboard-py3',
    packages=['em'],
    package_data={'': ['LICENSE', 'NOTICE'], 'em': ['emojis.json',]},
    include_package_data=True,
    entry_points = {
        'console_scripts': ['em=em:cli'],
    },
    install_requires=requires,
    license='ISC',
    zip_safe=False,
    classifiers=(
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    )
)
