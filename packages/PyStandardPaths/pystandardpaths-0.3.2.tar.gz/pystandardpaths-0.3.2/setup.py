#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import find_packages, setup


def get_version():
    code = None
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'standardpaths',
        '__init__.py',
    )
    with open(path) as f:
        for line in f:
            if line.startswith('VERSION'):
                code = line[len('VERSION = '):]
    return '.'.join([str(c) for c in eval(code)])


with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read().replace('.. :changelog:', '')


requirements = [
    'pathlib2; python_version < "3.4"',
    'enum34; python_version < "3.4"',
    'rubicon-objc; sys_platform == "darwin"',
]

test_requirements = [
    line for line in open('requirements.txt').read().split() if line
]


setup(
    name='pystandardpaths',
    version=get_version(),
    description=(
        'Cross-platform standard paths access in Python, based on '
        'QStandardPaths in Qt 5.'
    ),
    long_description=readme + '\n\n' + history,
    author='Tzu-ping Chung',
    author_email='uranusjr@gmail.com',
    url='https://github.com/uranusjr/pystandardpaths',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license='BSD',
    zip_safe=False,
    keywords='qstandardpaths',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
