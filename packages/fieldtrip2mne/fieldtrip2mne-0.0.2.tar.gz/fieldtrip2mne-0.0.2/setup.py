# -*- coding: UTF-8 -*-
# Copyright (c) 2018, Thomas Hartmann & Dirk Gütlin
#
# This file is part of the fieldtrip2mne Project, see: https://gitlab.com/obob/fieldtrip2mne
#
#    fieldtrip2mne is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    fieldtrip2mne is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with obob_subjectdb. If not, see <http://www.gnu.org/licenses/>.

from codecs import open

import os.path
from setuptools import setup

# find the location of this file
this_directory = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the Module Version from the VERSION file
with open(os.path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

# define required modules
required = [
    'mne',
    'pymatreader',
    'numpy>=1.13',
    'scipy',
    'matplotlib']

setup(
    name='fieldtrip2mne',
    version=version,
    packages=['fieldtrip2mne'],
    description='Convert MEG and EEG brain scan data from FieldTrip toolbox in Matlab to MNE toolbox in python.',
    long_description=long_description,
    url='https://gitlab.com/obob/fieldtrip2mne',
    license='GPL3',
    author='Thomas Hartmann & Dirk Gütlin',
    author_email='thomas.hartmann@th-ht.de',
    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python :: 2.7'],
    keywords='MNE FieldTrip converter MATLAB to Python',
    install_requires=required,
)
