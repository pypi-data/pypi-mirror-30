#!/usr/bin/env python

import sys
import os
from distutils.core import setup

import hostconf

# make this exist as a string so we can append to it
__doc__ = '''
'''

# slurp the top of the readme to be the long-description.
with open('README') as fd:
    _ = fd.readline()  # skip the heading
    _ = fd.readline()
    _ = fd.readline()
    for line in fd.readlines():
        if line.startswith('Origin'):
            break
        __doc__ += line

# append this
__doc__ += """Have a look at the README.md in the source repo.
"""

#
# Run the common utility
#
setup(
    name='hostconf',
    version=hostconf.version(),
    description='A host inspection/configuration tool to replace autoconf',
    long_description=__doc__,
    packages=[
        'hostconf',
        'hostconf.tests'
    ],
    url='https://github.com/mark-nicholson/python-hostconf',
    author='Mark Nicholson',
    author_email='nicholson.mark@gmail.com',
    license='BSD',
    python_requires='>=3.3',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
