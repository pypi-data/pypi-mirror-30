#!/usr/bin/env python

from setuptools import setup

setup(
    name='libfaketimefs-botocore',
    version='0.0.1',
    description='Patches botocore to work with libfaketimefs',
    author='Raymond Butcher',
    author_email='ray.butcher@claranet.uk',
    url='https://github.com/claranet/libfaketimefs-botocore',
    license='MIT License',
    packages=(
        'libfaketimefs_botocore',
    ),
    install_requires=(
        'botocore',
    ),
)
