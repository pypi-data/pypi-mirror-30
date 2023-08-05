# Copyright 2015-2017 Canonical Ltd.
#
# This file is part of juju-act, a juju plugin improving the usability
# of Juju actions from the command line.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from codecs import open
from os import path

import sys
sys.modules['yaml'] = sys  # Hack to allow build time import

import juju_act

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='juju-act',
    version=juju_act.__version__,
    author='Stuart Bishop',
    author_email='stuart.bishop@canonical.com',
    description='Juju plugin to improve the command line UI of Juju actions',
    url='https://launchpad.net/juju-act',
    long_description=long_description,
    license='GPLv3',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Plugins',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved '
                 ':: GNU General Public License v3 (GPLv3)',
                 'Operating System :: OS Independent',
                 'Topic :: System :: Installation/Setup',
                 'Topic :: Utilities',
                 'Programming Language :: Python :: 3'],
    keywords='juju',
    install_requires=['PyYAML'],
    py_modules=['juju_act'],
    entry_points={'console_scripts': ['juju-act = juju_act:act_cmd']})
