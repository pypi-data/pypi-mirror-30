#!/usr/bin/env python

import os
import sys

from archery import __version__ as version

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md', 'r') as f:
    readme = f.read()

# Publish helper
if sys.argv[-1] == 'build':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit(0)

if sys.argv[-1] == 'install':
    os.system('python setup.py sdist --formats=zip')
    sys.exit(0)

setup(
    name='pyArchery',
    packages=[
        'archery',
    ],
    version=version,
    description='Python library interacting to Archery Tool RESTFul API endpoints.',
    long_description=readme,
    author='Anand Tiwari',
    url='https://github.com/archerysec/',
    download_url='https://github.com/archerysec/archerysec-python-package/releases',
    license='MIT License',
    zip_safe=True,
    install_requires=['requests'],
    keywords=['pyArchery', 'api', 'security', 'software', 'ArcherySec'],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
    ]
)
