"""coauthor setup.py"""

import re
from codecs import open
from os import path
from setuptools import find_packages, setup


PACKAGE_NAME = 'coauthor'
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as fp:
    README = fp.read()
with open(path.join(HERE, PACKAGE_NAME, 'const.py'),
          encoding='utf-8') as fp:
    VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)


setup(name=PACKAGE_NAME,
      author='Bryce Boe',
      author_email='bbzbryce@gmail.com',
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Utilities'],
      description=('A tool that facilitates adding '
                   '`Co-authored-by: name <email>` lines in a user friendly '
                   'way to git commits.'),
      install_requires=['gitpython >=2.1.9, <3'],
      keywords='git github coauthor',
      license='Simplified BSD License',
      long_description=README,
      package_data={'': ['LICENSE.txt'], PACKAGE_NAME: ['*.ini']},
      packages=find_packages(exclude=['tests', 'tests.*']),
      setup_requires=['pytest-runner >=4.2, <5'],
      tests_require=['pytest >=3.5.0'],
      test_suite='tests',
      url='https://github.com/bboe/coauthor',
      version=VERSION)
