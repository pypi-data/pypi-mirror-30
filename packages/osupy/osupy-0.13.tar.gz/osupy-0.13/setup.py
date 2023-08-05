#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='osupy',
      version='0.13',
      url='https://github.com/Preta-Crowz/osupy',
      license='MIT',
      author='Preta',
      author_email='preta@crowz.r-e.kr',
      description='osu! Python API',
      packages=['osupy'],
      setup_requires=['requests>=2.13.0'],
      keywords=['osu','osupy']
     )