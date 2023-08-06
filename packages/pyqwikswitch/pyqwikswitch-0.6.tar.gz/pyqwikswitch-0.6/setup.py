#!/usr/bin/env python3
"""pyqwikswitch library setup."""
from setuptools import setup

REQUIREMENTS = ['requests']

setup(name='pyqwikswitch',
      version='0.6',
      description='Library to interface Qwikswitch USB Hub',
      url='https://github.com/kellerza/pyqwikswitch',
      download_url='https://github.com/kellerza/pyqwikswitch/tarball/0.6',
      author='Johann Kellerman',
      author_email='kellerza@gmail.com',
      license='MIT',
      packages=['pyqwikswitch'],
      install_requires=REQUIREMENTS,
      zip_safe=True)
