#!/usr/bin/python3

from setuptools import setup

setup(
  name='iprange',
  version='0.2',
  description='IP-Range generator',
  author='Philip Stoop',
  author_email='stoopphilip97@gmail.com',
  url='https://github.com/philip-s/py_iprange',
  download_url='https://github.com/philip-s/py_iprange/archive/0.2.tar.gz',
  py_modules=['iprange'],
  entry_points = {'console_scripts': ['iprange=iprange:main']}
)
