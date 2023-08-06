# -*- coding: utf-8 -*-
#
# Copyright 2017, 2018 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
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
"""Python SDK and CLI for the Renku platform."""

import os

from setuptools import find_packages, setup

readme = ''  # open('README.rst').read()
history = ''  # open('CHANGES.rst').read()

tests_require = [
]

extras_require = {
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name.startswith(':'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
]

install_requires = [
]

packages = find_packages()

# Get the version string. Cannot be done with import!
# g = {}
# with open(os.path.join('renku', 'version.py'), 'rt') as fp:
#     exec(fp.read(), g)
#     version = g['__version__']
version = '0.1.0.dev20180405'

setup(
    name='renku',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='Renku CLI',
    license='Apache License 2.0',
    author='Swiss Data Science Center',
    author_email='contact@datascience.ch',
    url='https://github.com/SwissDataScienceCenter/renku-python',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 1 - Planning',
    ],
)
