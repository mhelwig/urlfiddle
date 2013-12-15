#!/usr/bin/python
from distutils.core import setup
from setuptools import find_packages

setup(name='urlfiddle',
      version='0.1',
      description='URL generation and manipulation tool',
      author='Michael Helwig',
      author_email='info@jhp-consulting.eu',
      url='https://github.com/mhelwig/urlfiddle',
      license='MIT',
      scripts=['bin/urlfiddle'],
      packages=find_packages(exclude=('test')),
      
)
