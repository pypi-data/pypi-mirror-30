#coding=utf-8

import os
from setuptools import setup, find_packages
from ssdb import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

setup(
    name='ssdb-py3',
    version=__version__,
    description='Python3 client for SSDB',
    long_description=long_description,
    url='https://github.com/vmvz/ssdb-py3',
    author='dai3',
    author_email='github@dai3.com',
    maintainer='dai3',
    maintainer_email='github@dai3.com',
    zip_safe=False,
    include_package_data=True,
    keywords=['SSDB'],
    license='BSD-2',
    packages=['ssdb'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ]
)
    

