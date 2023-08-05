#!/usr/bin/env python3
"""
Presto setup
"""
# Imports
import os
import sys

# Check setup requirements
if sys.version_info < (3,4,0):
    sys.exit('At least Python 3.4.0 is required.\n')

try:
    from setuptools import setup
except ImportError:
    sys.exit('Please install setuptools before installing presto.\n')

try:
    from pip.req import parse_requirements
except ImportError:
    sys.exit('Please install pip before installing presto.\n')

# Get version, author and license information
info_file = os.path.join('presto', 'Version.py')
__version__, __author__, __license__ = None, None, None
try:
    exec(open(info_file).read())
except:
    sys.exit('Failed to load package information from %s.\n' % info_file)

if __version__ is None:
    sys.exit('Missing version information in %s\n.' % info_file)
if __author__ is None:
    sys.exit('Missing author information in %s\n.' % info_file)
if __license__ is None:
    sys.exit('Missing license information in %s\n.' % info_file)

# Load long package description
desc_files = ['README.rst', 'INSTALL.rst', 'NEWS.rst']
long_description = '\n\n'.join([open(f, 'r').read() for f in desc_files])

# Define installation path for commandline tools
scripts = ['AlignSets.py',
           'AssemblePairs.py',
           'BuildConsensus.py',
           'ClusterSets.py',
           'CollapseSeq.py',
           'ConvertHeaders.py',
           'EstimateError.py',
           'FilterSeq.py',
           'MaskPrimers.py',
           'PairSeq.py',
           'ParseHeaders.py',
           'ParseLog.py',
           'SplitSeq.py',
           'UnifyHeaders.py']
install_scripts = [os.path.join('bin', s) for s in scripts]

# TODO: check pip version to avoid problem with parse_requirements(session=False)
# Parse requirements
if os.environ.get('READTHEDOCS', None) == 'True':
    # Set empty install_requires to get install to work on readthedocs
    install_requires = []
else:
    require_file = 'requirements.txt'
    try:
        requirements = parse_requirements(require_file, session=False)
    except TypeError:
        requirements = parse_requirements(require_file)
    install_requires = [str(r.req) for r in requirements]

# Setup
setup(name='presto',
      version=__version__,
      author=__author__,
      author_email='immcantation@googlegroups.com',
      description='A bioinformatics toolkit for processing high-throughput lymphocyte receptor sequencing data.',
      long_description=long_description,
      zip_safe=False,
      license=__license__,
      url='http://presto.readthedocs.io',
      download_url='https://bitbucket.org/kleinstein/presto/downloads',
      keywords='bioinformatics immunoglobulin lymphocyte sequencing',
      install_requires=install_requires,
      packages=['presto'],
      package_dir={'presto': 'presto'},
      scripts=install_scripts,
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Scientific/Engineering :: Bio-Informatics'])
