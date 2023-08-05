#!/usr/bin/env python

from setuptools import setup

import versioneer

setup(
    name='test-versioneer-setup-nathanwilk7',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=[
        'test_versioneer_setup_nathanwilk7'
    ],
    description="Test with versioneer, setup.py, uploaded to pypi, then to conda, then taggable, etc.",
    author="Recursion Pharmaceuticals",
    author_email="dev@recursionpharma.com",
)
