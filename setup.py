#!/usr/bin/python

# Copyright 2013 Lou King
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ez_setup
import glob
import pdb

# home grown
import version

ez_setup.use_setuptools()
from setuptools import setup, find_packages

def globit(dir, filelist):
    outfiles = []
    for file in filelist:
        filepath = '{0}/{1}'.format(dir,file)
        gfilepath = glob.glob(filepath)
        for i in range(len(gfilepath)):
            f = gfilepath[i][len(dir)+1:]
            gfilepath[i] = '{0}/{1}'.format(dir,f)  # if on windows, need to replace backslash with frontslash
            outfiles += [gfilepath[i]]
    return (dir, outfiles)

setup(
    name = "runningclub",
    version = version.__version__,
    packages = find_packages(),
#    include_package_data = True,
    scripts = [
        'runningclub/agegrade.py',
        'runningclub/analyzeeventmembers.py',
        'runningclub/analyzemembership.py',
        'runningclub/exportresults.py',
        'runningclub/genagtables.py',
        'runningclub/getresultsmembers.py',
        'runningclub/importmembers.py',
        'runningclub/importraces.py',
        'runningclub/importresults.py',
        'runningclub/listraces.py',
        'runningclub/rcadminapprove.py',
        'runningclub/rcadminconfig.py',
        'runningclub/rcuserconfig.py',
        'runningclub/renderrace.py',
        'runningclub/renderstandings.py',
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        #'loutilities>=0.5.0',
        'xlrd>=0.8.0',
        ],

    # If any package contains any of these file types, include them:
    data_files = ([
            globit('runningclub', ['*.conf','*.pyc','*.pyd','*.dll','*.h','*.xlsx']),
            globit('runningclub/doc/source', ['*.txt', '*.rst', '*.html', '*.css', '*.js', '*.png', '*.py', ]),
            globit('runningclub/doc/build/html', ['*.txt', '*.rst', '*.html', '*.css', '*.js', '*.png', ]),
            globit('runningclub/doc/build/html/_sources', ['*.txt', '*.rst', '*.html', '*.css', '*.js', '*.png', ]),
            globit('runningclub/doc/build/html/_static', ['*.txt', '*.rst', '*.html', '*.css', '*.js', '*.png', ]),
            globit('runningclub/doc/build/html/_images', ['*.png', ]),
        ]),


    entry_points = {
        'console_scripts': [
            'agegrade = runningclub.agegrade:main',
            'analyzeeventmembers = runningclub.analyzeeventmembers:main',
            'analyzemembership = runningclub.analyzemembership:main',
            'exportresults = runningclub.exportresults:main',
            'genagtables = runningclub.genagtables:main',
            'getresultsmembers = runningclub.getresultsmembers:main',
            'importmembers = runningclub.importmembers:main',
            'importraces = runningclub.importraces:main',
            'importresults = runningclub.importresults:main',
            'listraces = runningclub.listraces:main',
            'rcadminapprove = runningclub.rcadminapprove:main',
            'rcadminconfig = runningclub.rcadminconfig:main',
            'rcuserconfig = runningclub.rcuserconfig:main',
            'renderrace = runningclub.renderrace:main',
            'renderstandings = runningclub.renderstandings:main',
        ],
    },


    zip_safe = False,

    # metadata for upload to PyPI
    description = 'data analysis and automation for a running club',
    license = 'Apache License, Version 2.0',
    author = 'Lou King',
    author_email = 'lking@pobox.com',
    url = 'http://github.com/louking/runningclub', 
    # could also include long_description, download_url, classifiers, etc.
)

