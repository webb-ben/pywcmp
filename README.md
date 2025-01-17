# pywcmp

[![Build Status](https://github.com/wmo-im/pywcmp/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/pywcmp/actions)

# WMO Core Metadata Profile Test Suite

pywcmp provides validation and quality assessment capabilities for the [WMO
WIS](https://community.wmo.int/activity-areas/wis/wis-overview) Core Metadata
Profile (WCMP).

- validation against [WCMP 1.3](http://wis.wmo.int/2013/metadata/version_1-3-0/WMO_Core_Metadata_Profile_v1.3_Part_1.pdf), specifically [Part 2](http://wis.wmo.int/2013/metadata/version_1-3-0/WMO_Core_Metadata_Profile_v1.3_Part_2.pdf), Section 2, implementing an executable test suite against the ATS
- quality assessement against the [WCMP Key Performance Indicators](https://community.wmo.int/activity-areas/wis/wis-metadata-kpis)

## Installation

### pip

Install latest stable version from [PyPI](https://pypi.org/project/pywcmp).

```bash
pip3 install pywcmp
```

### From source

Install latest development version.

```bash
python3 -m venv pywcmp
cd pywcmp
. bin/activate
git clone https://github.com/wmo-im/pywcmp.git
cd pywcmp
pip3 install -r requirements.txt
python3 setup.py build
python3 setup.py install
```

## Running

From command line:
```bash
# fetch version
pywcmp --version

# abstract test suite

# validate metadata against abstract test suite (file on disk)
pywcmp ats validate --file /path/to/file.xml

# validate metadata against abstract test suite (URL)
pywcmp ats validate --url http://example.org/path/to/file.xml

# adjust debugging messages (CRITICAL, ERROR, WARNING, INFO, DEBUG) to stdout
pywcmp ats validate --url http://example.org/path/to/file.xml --verbosity DEBUG

# write results to logfile
pywcmp ats validate --url http://example.org/path/to/file.xml --verbosity DEBUG --logfile /tmp/foo.txt

# key performance indicators

# all key performance indicators at once # note: running KPIs automatically runs the ats
pywcmp kpi validate --url http://example.org/path/to/file.xml --verbosity DEBUG

# all key performance indicators at once, in summary
pywcmp kpi validate --url http://example.org/path/to/file.xml --verbosity DEBUG --summary

# all key performance indicators at once, with scoring rubric grouping
pywcmp kpi validate --url http://example.org/path/to/file.xml --verbosity DEBUG --group

# selected key performance indicator
pywcmp kpi validate --kpi 4 -f /path/to/file.xml -v INFO

# WIS topic hierarchies

# validate a WIS 2.0 topic hierarchy
pywcmp topics validate -th wis2.a.cache.CAN

# list children of a given WIS 2.0 topic hierarchy level
pywcmp topics list -th wis2.a

```

## Using the API
```pycon
>>> # test a file on disk
>>> from lxml import etree
>>> from pywcmp.ats import ats
>>> exml = etree.parse('/path/to/file.xml')
>>> # test ATS
>>> ts = ats.WMOCoreMetadataProfileTestSuite13(exml)
>>> ts.run_tests()  # raises ValueError error stack on exception
>>> # test a URL
>>> from urllib2 import urlopen
>>> from StringIO import StringIO
>>> content = StringIO(urlopen('http://....').read())
>>> exml = etree.parse(content)
>>> ts = ats.WMOCoreMetadataProfileTestSuite13(exml)
>>> ts.run_tests()  # raises ValueError error stack on exception
>>> # handle ats.TestSuiteError
>>> # ats.TestSuiteError.errors is a list of errors
>>> try:
...    ts.run_tests()
... except ats.TestSuiteError as err:
...    print('\n'.join(err.errors))
>>> ...
>>> # test KPI
>>> from pywcmp.kpi import WMOCoreMetadataProfileKeyPerformanceIndicators
>>> kpis = WMOCoreMetadataProfileKeyPerformanceIndicators(exml)
>>> results = kpis.evaluate()
>>> results['summary']
>>> # scoring rubric
>>> grouped = group_kpi_results(results)
```

## Development

```bash
python3 -m venv pywcmp
cd pywcmp
source bin/activate
git clone https://github.com/wmo-im/pywcmp.git
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
python3 setup.py install
```

### Running tests

```bash
# via setuptools
python3 setup.py test
# manually
python3 tests/run_tests.py
```

## Releasing

```bash
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/wmo-im/pywcmp/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Ján Osuský](https://github.com/josusky)
