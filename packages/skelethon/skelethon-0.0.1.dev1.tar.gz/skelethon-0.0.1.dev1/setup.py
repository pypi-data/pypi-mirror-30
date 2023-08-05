# -*- coding: utf-8 -*-
"""Setup file for the skelethon."""

from os.path import dirname, exists, join, realpath
from setuptools import setup, find_packages


########################################################################
# Contact Information
########################################################################

URL = 'https://www.github.com/mplanchard/skelethon'
AUTHOR = 'Matthew Planchard'
EMAIL = 'msplanchard@gmail.com'


########################################################################
# Package Description
########################################################################

NAME = 'skelethon'
SHORT_DESC = 'Make a SKELEton for pyTHON projects :)'
LONG_DESC = SHORT_DESC
KEYWORDS = [
    'python',
    'setup',
    'project',
    'packaging',
    'versioning',
    'skeleton',
]
CLASSIFIERS = [
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers for all
    # available setup classifiers
    'Development Status :: 1 - Planning',
    # 'Development Status :: 2 - Pre-Alpha',
    # 'Development Status :: 3 - Alpha',
    # 'Development Status :: 4 - Beta',
    # 'Development Status :: 5 - Production/Stable',
    # 'Development Status :: 6 - Mature',
    # 'Framework :: AsyncIO',
    # 'Framework :: Flask',
    # 'Framework :: Sphinx',
    # 'Environment :: Web Environment',
    'Intended Audience :: Developers',
    # 'Intended Audience :: End Users/Desktop',
    # 'Intended Audience :: Science/Research',
    # 'Intended Audience :: System Administrators',
    # 'License :: Other/Proprietary License',
    # 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    # 'Operating System :: MacOS :: MacOS X
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    # 'Programming Language :: Python :: 3 :: Only',
    # 'Programming Language :: Python :: Implementation :: PyPy',
]


########################################################################
# Dependency Specification
########################################################################

PACKAGE_DEPENDENCIES = [
    'click',
    'jinja2',
]
SETUP_DEPENDENCIES = []
TEST_DEPENDENCIES = [
    'pytest',
]
EXTRAS_DEPENDENCIES = {}


########################################################################
# Package Extras
########################################################################

ENTRY_POINTS = {}
PACKAGE_DATA = {}


########################################################################
# Setup Logic
########################################################################

PACKAGE_DIR = realpath(dirname(__file__))


REQ_FILE = join(PACKAGE_DIR, 'requirements_unfrozen.txt')
if exists(REQ_FILE):
    with open(join(PACKAGE_DIR, 'requirements.txt')) as reqfile:
        for ln in (l.strip() for l in reqfile):
            if ln and not ln.startswith('#'):
                PACKAGE_DEPENDENCIES.append(ln)


__version__ = '0.0.0'

cwd = dirname(realpath(__file__))

with open(join(cwd, '{}/version.py'.format(NAME))) as version_file:
    for line in version_file:
        # This will __version__ and __version_info__ variables locally
        if line.startswith('__'):
            exec(line)

setup(
    name=NAME,
    version=__version__,
    description=SHORT_DESC,
    long_description=LONG_DESC,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    package_data=PACKAGE_DATA,
    packages=find_packages(exclude=['*.tests', '*.tests.*']),
    install_requires=PACKAGE_DEPENDENCIES,
    setup_requires=SETUP_DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    extras_require=EXTRAS_DEPENDENCIES,
    entry_points=ENTRY_POINTS,
)
