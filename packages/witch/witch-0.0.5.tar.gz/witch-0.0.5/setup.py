#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from setuptools import setup
from setuptools import find_packages
# from setuptools.command.install import install as _install
# from setuptools.command.develop import develop as _develop

# here = os.getcwd()
#
# with open(os.path.join(here, 'witch', '__version__')) as f:
#     __version__ = f.read().strip()

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['future', 'Click>=6.0',]

setup_requirements = ['future']

test_requirements = [ ]


setup(
    author="James Draper",
    author_email='james.draper@protonmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Platform independent which",
    entry_points={
        'console_scripts': [
            'which=witch.cli:main',
            'witch=which.cli:main',
            # 'where=witch.cli:main',
            # 'whereis=witch.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='witch',
    name='witch',
    packages=find_packages(include=['witch']),
    # package_data = {'witch': ['__version__']},
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/draperjames/witch',
    version='0.0.5',
    zip_safe=False,
)
