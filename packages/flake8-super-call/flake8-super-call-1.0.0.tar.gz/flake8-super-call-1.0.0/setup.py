#!/usr/bin/env python

import re

from setuptools import setup


def get_version(filename):
    f = open(filename).read()
    return re.search('__version__ = [\'"]([^\'"]+)[\'"]', f).group(1)


version = get_version('flake8_super_call.py')
description = open('README.rst').read()
url = 'https://github.com/DragosOprica/flake8-super-call'

setup(
    name='flake8-super-call',
    license='MIT',
    version=version,
    description='flake8 super call checker',
    long_description=description,
    author='Dragos Oprica',
    author_email='dragos.oprica92@gmail.com',
    keywords='flake8 super',
    url=url,
    download_url=url + '/tarball/' + version,
    entry_points={'flake8.extension': ['S777 = flake8_super_call:Checker']},
    py_modules=['flake8_super_call'],
    install_requires=['flake8>=3.0.0'],
    tests_require=['flake8>=3.0.0'],
    test_suite='tests',
    zip_safe=True,
    classifiers=[
        'Environment :: Console',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
