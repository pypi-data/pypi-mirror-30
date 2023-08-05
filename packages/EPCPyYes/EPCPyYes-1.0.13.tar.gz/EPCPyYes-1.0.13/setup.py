#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import EPCPyYes
from setuptools import setup

def get_data_files(path):
    data_files = []
    directories = glob.glob(path)
    for directory in directories:
        files = glob.glob(directory + '*')
        data_files.append((directory, files))
    return data_files


with open('README.rst') as readme_file:
    readme = readme_file.read()


requirements = [
    'Jinja2==2.9.4',
    'commonmark',
    'lxml==3.7.0',
]

test_requirements = requirements + [
    'Jinja2==2.9.4',
    'commonmark',
    'lxml==3.7.0',
]

setup(
    name='EPCPyYes',
    version='1.0.13',
    description="EPCIS Python module for quickly developing "
                "EPCIS-enabled applications.",
    long_description=readme,
    author="Rob Magee",
    author_email='slab@serial-lab.com',
    maintainer='SerialLab Corp',
    url='https://gitlab.com/serial-lab/EPCPyYes',
    packages=[
        'EPCPyYes', 'EPCPyYes.core', 'EPCPyYes.core.v1_2',
        'EPCPyYes.core.v1_2.CBV', 'EPCPyYes.core.tests'
    ],
    package_dir={'EPCPyYes':
                     'EPCPyYes'},
    entry_points={
    },
    data_files=get_data_files('EPCPyYes/templates/epcis/') + \
               get_data_files('EPCPyYes/core/tests/schemas/'),
    include_package_data=True,
    install_requires=requirements,
    license="GNU Affero General Public License v3",
    zip_safe=False,
    keywords='EPCPyYes EPCIS GS1 RFID Serialization',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='EPCPyYes.core.tests',
    tests_require=test_requirements
)
