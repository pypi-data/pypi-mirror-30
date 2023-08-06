import ast
import re
import docutils

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

NAME = 'baka_tenshi'
DESC = 'Baka: Skeleton framework built top of pyramid, baka_tenshi for sqlalchemy'
AUTHOR = 'Nanang Suryadi'
AUTHOR_EMAIL = 'nanang.jobs@gmail.com'
URL = 'https://github.com/baka-framework/baka_tenshi'
DOWNLOAD_URL = 'https://github.com/baka-framework/baka_tenshi/archive/1.0.0.tar.gz'
LICENSE = 'MIT'
KEYWORDS = ['model', 'sqlalchemy', 'framework']
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Pyramid',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Operating System :: OS Independent',
]
INSTALL_REQUIRES = [
    'setuptools',
    'trafaret',
    'pyramid',
    'sqlalchemy',
    'zope.sqlalchemy',
    'transaction',
    'pyramid_retry',
    'pyramid_tm',
    'awesome-slugify',
    'passlib',
    'argon2_cffi'
]
EXTRAS_REQUIRE = {}
ENTRY_POINTS = {}


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('baka_tenshi/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(name=NAME,
      version=version,
      description=DESC,
      long_description=long_description,
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      entry_points=ENTRY_POINTS,
      packages=find_packages(include=['baka_tenshi', 'baka_tenshi.*']),
      zip_safe=False)
