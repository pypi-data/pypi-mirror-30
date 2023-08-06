# -*- coding: UTF-8 -*-
# Copyright (c) 2018, Thomas Hartmann & Dirk Gütlin
# All rights reserved.
#
# This file is part of the fieldtrip2mne Project, see: https://gitlab.com/obob/fieldtrip2mne
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
    license='BSD (2 clause)',
    author='Thomas Hartmann & Dirk Gütlin',
    author_email='thomas.hartmann@th-ht.de',
    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 2.7'],
    keywords='MNE FieldTrip converter MATLAB to Python',
    install_requires=required,
)
