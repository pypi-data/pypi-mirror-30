# -*- encoding: utf-8 -*-
import os
import re

from setuptools import setup

PACKAGE_NAME = 'coke'


def get_version():
    version_py_path = os.path.join(os.path.dirname(__file__), PACKAGE_NAME, 'version.py')
    pattern = re.compile(r'''^__version__\s*=\s*(?P<quote>['"])(?P<version>[^'"]+)(?P=quote)\s*(?:#.*)?$''')
    with open(version_py_path, 'r', encoding='utf-8') as fob:
        for line in fob:
            match = pattern.match(line)
            if match is not None:
                return match.group('version')
    raise ValueError('No version found')


VERSION = get_version()


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author='Mathias Fröjdman',
    author_email='mwf@iki.fi',
    description='Python GraphQL library',
    keywords=['graphql'],
    project_urls={
        'Source': 'https://github.com/mwfrojdman/coke',
        'Tracker': 'https://github.com/mwfrojdman/coke/issues',
    },
    download_url='https://github.com/mwfrojdman/coke/archive/{}.tar.gz'.format(VERSION),
    packages=[
        'coke',
    ],
    package_data={'': ['LICENSE.txt']},
    python_requires='>=3.5',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    platforms='all'
)
