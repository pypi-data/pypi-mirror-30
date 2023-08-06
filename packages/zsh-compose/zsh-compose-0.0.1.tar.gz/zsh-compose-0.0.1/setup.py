#!/usr/bin/env python3
# Copyright 2018 Peijun Ma
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import configparser
import json
import sys
from pathlib import Path
from shlex import split
from subprocess import run

from setuptools import setup

HERE = Path(__file__).parent

if sys.argv[-1] == 'publish':
    run(split('python setup.py sdist bdist_wheel'))
    run(split('twine upload dist/*'))
    exit()

config = configparser.ConfigParser()
config.read(HERE / 'Pipfile')
packages = list(config['packages'])

lock = json.loads((HERE / 'Pipfile.lock').read_text())

reqs = [
    key + val['version'].replace('==', '>=')
    for key, val in lock['default'].items()
    if key in packages
]

about = {}
exec((HERE / 'zsh_compose' / '__version__.py').read_text(), about)
readme = (HERE / 'README.md').read_text()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    author=about['__author__'],
    author_email=about['__author_email__'],
    license=about['__license__'],
    url=about['__url__'],
    py_modules=[
        'main',
    ],
    packages=[
        'zsh_compose',
    ],
    install_requires=reqs,
    package_data={'': ['README.md', 'LICENSE', 'Pipfile', 'Pipfile.lock']},
    include_package_data=True,
    python_requires=">=3.6",
    entry_points='''
        [console_scripts]
        zsh-compose=main:main
    ''',
    classifiers=(
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ),
)
