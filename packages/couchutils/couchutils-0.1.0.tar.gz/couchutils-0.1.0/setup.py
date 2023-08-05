#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('couchutils/__version__.py') as fp:
    about = {}
    exec(fp.read(), about)

with open('README.rst') as fp:
    readme = fp.read()

with open('HISTORY.rst') as fp:
    history = fp.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description='\n\n'.join([readme, history]),
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['couchutils'],
    include_package_data=True,
    install_requires=['pathlib2; python_version == "2.7"', 'simplejson'],
    license=about['__license__'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    setup_requires=['pytest-runner'],
    test_suite='tests',
    tests_require=['pytest'],
)
