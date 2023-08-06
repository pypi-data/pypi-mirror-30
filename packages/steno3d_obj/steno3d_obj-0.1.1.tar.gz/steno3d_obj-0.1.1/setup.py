#!/usr/bin/env python
'''
    steno3d_obj: Steno3D parser plugin for Wavefront .obj files
'''

from distutils.core import setup
from setuptools import find_packages

CLASSIFIERS = [
'Development Status :: 4 - Beta',
'Programming Language :: Python',
'Topic :: Scientific/Engineering',
'Topic :: Scientific/Engineering :: Mathematics',
'Topic :: Scientific/Engineering :: Physics',
'Operating System :: Microsoft :: Windows',
'Operating System :: POSIX',
'Operating System :: Unix',
'Operating System :: MacOS',
'Natural Language :: English',
]

with open('README.rst') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

setup(
    name = 'steno3d_obj',
    version = '0.1.1',
    packages = find_packages(exclude=('tests',)),
    install_requires = ['numpy>=1.7',
                        'steno3d>=0.2.6'],
    author = 'Seequent',
    author_email = 'support@steno3d.com',
    description = 'steno3d_obj',
    long_description = LONG_DESCRIPTION,
    keywords = 'visualization',
    url = 'https://steno3d.com/',
    download_url = 'http://github.com/seequent/steno3d-obj',
    classifiers=CLASSIFIERS,
    platforms = ['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    license = 'MIT License',
    use_2to3 = False,
)
