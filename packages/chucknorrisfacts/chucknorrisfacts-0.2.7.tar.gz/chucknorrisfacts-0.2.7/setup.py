#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'requests>=2.18']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Jose R. Zapata",
    author_email='jjrzg@hotmail.com', 
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Display a random Chuck Norris Joke",
    entry_points={
        'console_scripts': [
            'chucknorrisfacts=chucknorrisfacts.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['chuck', 'norris', 'jokes'],
    name='chucknorrisfacts',
    packages=find_packages(include=['chucknorrisfacts']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/JoseRZapata/chucknorrisfacts',
    version='0.2.7',
    zip_safe=False,
)
