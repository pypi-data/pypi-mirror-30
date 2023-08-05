#!/usr/bin/python3

import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''

setup(
    name='fullcolor',
    version='0.2.1',
    description='Provides an easy way to print full 24bit colors in terminals that support it.',
    long_description=README + '\n\n' + CHANGES,
    url='https://github.com/eternali/fullcolor',
    author='Conrad Heidebrecht',
    author_email='conrad.heidebrecht@gmail.com',
    platforms='linux',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='color colour terminal logging',
    py_modules=['fullcolor'],
    install_requires=[]
)
