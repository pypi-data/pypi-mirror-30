#!/usr/bin/env python3
# python setup.py sdist
# twine upload dist/*
"""pyqwikswitch library setup."""
from setuptools import setup

REQUIREMENTS = ['attrs', 'requests']

setup(name='pyqwikswitch',
      version='0.71',
      description='Library to interface Qwikswitch USB Hub',
      url='https://github.com/kellerza/pyqwikswitch',
      download_url='https://github.com/kellerza/pyqwikswitch/tarball/0.71',
      author='Johann Kellerman',
      author_email='kellerza@gmail.com',
      license='MIT',
      packages=['pyqwikswitch'],
      install_requires=REQUIREMENTS,
      zip_safe=True)
