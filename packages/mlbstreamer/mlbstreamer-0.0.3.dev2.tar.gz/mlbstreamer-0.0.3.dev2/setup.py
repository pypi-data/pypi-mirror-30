#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
from os import path
from glob import glob

name = "mlbstreamer"
setup(name=name,
      version="0.0.3.dev2",
      description="MLB.tv Stream Browser",
      author="Tony Cebzanov",
      author_email="tonycpsu@gmail.com",
      url="https://github.com/tonycpsu/mlbstreamer",
      classifiers=[
          "Environment :: Console",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Intended Audience :: End Users/Desktop"
      ],
      license = "GPLv2",
      packages=find_packages(),
      include_package_data=True,
      install_requires = [
          "six",
          "requests",
          "lxml",
          "pytz",
          "tzlocal",
          "pymemoize",
          "orderedattrdict",
          "pyyaml",
          "py-dateutil",
          "streamlink",
          "prompt_toolkit"
      ],
      extras_require={
          'gui':  [
              "urwid",
              "urwid_utils==0.1.1.dev0",
              "panwid==0.2.2.dev5",
          ],
      },
      entry_points = {
          "console_scripts": [
              "mlbstreamer=mlbstreamer.__main__:main",
              "mlbplay=mlbstreamer.play:main"
          ],
      }
     )
