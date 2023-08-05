#!/usr/bin/python3

from setuptools import setup

setup(
  name='iprange',
  version='0.2.1',
  description='IP-Range generator',
  author='Philip Stoop',
  author_email='stoopphilip97@gmail.com',
  url='https://github.com/philip-s/py_iprange',
  packages=['iprange'],
  entry_points = {'console_scripts': ['iprange=iprange:main']}
)
