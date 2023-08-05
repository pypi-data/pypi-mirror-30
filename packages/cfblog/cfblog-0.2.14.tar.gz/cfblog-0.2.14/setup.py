# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

from setuptools import find_packages, setup

try:
    long_description = open('README.rst', 'rt').read()
except Exception:
    long_description = ""

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="cfblog",
    description="Awesome CMS for Django",
    long_description=long_description,

    version="0.2.14",
    author='Vinay Karanam, Ashish Nayan',
    author_email="vinayinvicible@gmail.com, nayanashish@gmail.com",

    url='https://github.com/Coverfox/cfblog/',
    license='BSD',

    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    zip_safe=True,
)
