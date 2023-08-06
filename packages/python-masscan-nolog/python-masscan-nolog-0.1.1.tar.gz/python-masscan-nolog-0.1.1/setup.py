#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup, Extension

masscan = Extension('masscan', sources=['masscan/masscan.py', 'masscan/__init__.py'])

from masscan import __version__
from masscan import __author__

# Install : python setup.py install
# Register : python setup.py register

#  platform = 'Unix',


setup(
    name='python-masscan-nolog',
    version=__version__,
    author=__author__,
    author_email='norkus.juozas@gmail.com',
    license='LICENSE',
    keywords="masscan, portscanner",
    platforms=[
        "Operating System :: OS Independent",
        ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Firewalls",
        "Topic :: System :: Networking :: Monitoring",
        ],
    packages=['masscan'],
    url='https://github.com/no-references/python-masscan',
    bugtrack_url='https://github.com/no-references/python-masscan',
    description='Fork of python-masscan with logging disabled',
)
