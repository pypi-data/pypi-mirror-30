#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dist = setup(
    name='im_futuregcscompose',
    version='0.1.1',
    description='function for composing an folder full of text files, into one text file, in gcs, for Google App Engine, Python standard environment',
    author='Emlyn O\'Regan',
    author_email='emlynoregan@gmail.com',
    url='https://github.com/emlynoregan/im_futuregcscompose', 
    license='../LICENSE.txt',
    packages=['im_futuregcscompose'],
    install_requires=['im_util', 'google-cloud-storage', 'im_future'],
    long_description=open('../README.md').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
    ]
)
