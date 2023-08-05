#!/usr/bin/env python3
# -*- coding: utf8 -*-

from setuptools import setup, find_packages


setup(
    name='triplecask',
    version='0.5.0',
    author='Mihir Singh (@citruspi)',
    author_email='pypi.service@mihirsingh.com',
    packages=find_packages(),
    python_requires='>=3.6',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite='nose.collector',
    extras_require={
        'dev': [
            'nose',
            'coverage'
        ],
        'pyopenssl': [
            'pyopenssl'
        ]
    }
)
