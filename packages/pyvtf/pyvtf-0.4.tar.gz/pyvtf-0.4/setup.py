#*****************************************************************
# terraform-provider-vcloud-director
# Copyright (c) 2017 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
#*****************************************************************

import pyvtf
from os import path
from codecs import open
from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    required_packages = f.readlines()

required_packages = [package.strip() for package in required_packages]
custom_packages = ['pyvtf', 'pyvtf.proto']

setup(
    name='pyvtf',
    version=pyvtf.__VERSION__,
    description='A Terrform Service Provider for VMware vCloud Director',
    long_description=long_description,
    url='https://github.com/vmware/terraform-provider-vcloud-director',
    author='pyvtf.vmware',
    author_email='srinarayana@vmware.com',
    license='BSD-2 License',
    keywords='terraform vcloud director vcd vmware',
    install_requires=required_packages,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['pyvtf=pyvtf.command_line:main'],
    },
    packages=custom_packages,
    project_urls={
        'Bug Reports': 'https://github.com/vmware/terraform-provider-vcloud-director/issues',
        'Source': 'https://github.com/vmware/terraform-provider-vcloud-director',
    },
)
