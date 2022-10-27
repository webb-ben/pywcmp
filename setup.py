###############################################################################
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2022 Tom Kralidis
# Copyright (c) 2022 Government of Canada
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import io
import json
import os
import re
from setuptools import Command, find_packages, setup
import sys
import zipfile

from lxml import etree

from pywcmp.util import get_userdir, urlopen_


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable, os.path.join('tests',
                                 'run_tests.py')])
        raise SystemExit(errno)


def read(filename, encoding='utf-8'):
    """read file contents"""
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with io.open(full_path, encoding=encoding) as fh:
        contents = fh.read().strip()
    return contents


def get_package_version():
    """get version from top-level package init"""
    version_file = read('pywcmp/__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


USERDIR = get_userdir()

WCMP1_FILES = f'{USERDIR}{os.sep}wcmp-1.3'
WCMP2_FILES = f'{USERDIR}{os.sep}wcmp-2.0'
WIS2_TOPICS_FILES = f'{USERDIR}{os.sep}topic-hierarchy'

KEYWORDS = [
    'WMO',
    'Metadata',
    'WIS',
    'Test Suite',
]

DESCRIPTION = 'A Python implementation of the test suite for WMO Core Metadata Profile'  # noqa

# ensure a fresh MANIFEST file is generated
if (os.path.exists('MANIFEST')):
    os.unlink('MANIFEST')


print('Caching schemas, codelists and topic hierarchy')

if not os.path.exists(WCMP1_FILES):
    os.makedirs(WCMP1_FILES, exist_ok=True)

    print(f'Downloading WCMP1 schemas and codelists to {WCMP1_FILES}')
    ZIPFILE_URL = 'https://wis.wmo.int/2011/schemata/iso19139_2007/19139.zip'
    FH = io.BytesIO(urlopen_(ZIPFILE_URL).read())
    with zipfile.ZipFile(FH) as z:
        z.extractall(WCMP1_FILES)
    CODELIST_URL = 'https://wis.wmo.int/2012/codelists/WMOCodeLists.xml'

    schema_filename = f'{WCMP1_FILES}{os.sep}WMOCodeLists.xml'

    with open(schema_filename, 'wb') as f:
        f.write(urlopen_(CODELIST_URL).read())

    # because some ISO instances ref both gmd and gmx, create a
    # stub xsd in order to validate
    SCHEMA = etree.Element('schema',
                           elementFormDefault='qualified',
                           version='1.0.0',
                           nsmap={None: 'http://www.w3.org/2001/XMLSchema'})

    schema_wrapper_filename = f'{WCMP1_FILES}{os.sep}iso-all.xsd'

    with open(schema_wrapper_filename, 'wb') as f:
        for uri in ['gmd', 'gmx']:
            namespace = f'http://www.isotc211.org/2005/{uri}'
            schema_location = f'schema/{uri}/{uri}.xsd'

            etree.SubElement(SCHEMA, 'import',
                             namespace=namespace,
                             schemaLocation=schema_location)
        f.write(etree.tostring(SCHEMA, pretty_print=True))

if not os.path.exists(WIS2_TOPICS_FILES):
    print('Downloading topic hierarchies')
    os.makedirs(WIS2_TOPICS_FILES, exist_ok=True)

    response = urlopen_('https://api.github.com/repos/wmo-im/wis2-topic-hierarchy/contents/topic-hierarchy') # noqa
    response = json.loads(response.read())

    for item in response:
        if item.get('name').endswith('.csv'):
            filename = item['name']
            th_filepath = f'{WIS2_TOPICS_FILES}{os.sep}{filename}'
            with open(th_filepath, 'wb') as f:
                f.write(urlopen_(item['download_url']).read())


setup(
    name='pywcmp',
    version=get_package_version(),
    description=DESCRIPTION.strip(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    platforms='all',
    keywords=' '.join(KEYWORDS),
    author='Tom Kralidis',
    author_email='tomkralidis@gmail.com',
    maintainer='Tom Kralidis',
    maintainer_email='tomkralidis@gmail.com',
    url='https://github.com/wmo-im/pywcmp',
    install_requires=read('requirements.txt').splitlines(),
    packages=find_packages(),
    package_data={'pywcmp': ['dictionary.txt']},
    entry_points={
        'console_scripts': [
            'pywcmp=pywcmp:cli'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    cmdclass={'test': PyTest},
    test_suite='tests.run_tests'
)
