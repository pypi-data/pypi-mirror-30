#!/usr/bin/env python3
#setup.py
import sys, os
from distutils.core import setup
from setuptools import setup
from setuptools.command.install import install
from subprocess import check_call
from pics2word.WriteHelp import writehelp

__version__ = "0.9.7"

#def readme():
#    with open(r"docs/README.md") as f:
#        return f.read()

setup(
    name = "pics2word",
    description='A command line program to copy a large number of pictures into a word document.',
    version=__version__,
    url='https://github.com/Ghostom998/pics2word.git',
    author='Thomas Roberts',
    author_email='tom_roberts.1992@hotmail.co.uk',
    license='GNU GPL V3.0',
    packages=['pics2word'],
    install_requires=['docx','python-docx','datetime'], # Dependencies
    python_requires='>=3.6.4',
    include_package_data=True,
    zip_safe=True,
#   long_description=readme(),
    entry_points = {
        'console_scripts': ['pics2word=pics2word.__init__:main'],
    },
    classifiers=[
    'Development Status :: 1 - Planning',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3.6',
    'Environment :: Console',
    'Topic :: Office/Business :: Office Suites',
    ]
)