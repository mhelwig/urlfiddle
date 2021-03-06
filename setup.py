#!/usr/bin/python
from distutils.core import setup
from setuptools import find_packages

setup(name='urlfiddle',
      version='0.2',
      description='URL generation and manipulation tool',
      author='Michael Helwig',
      author_email='info@jhp-consulting.eu',
      url='https://github.com/mhelwig/urlfiddle',
      license='MIT',
      scripts=['bin/urlfiddle'],
      extras_require = {
        'analyze':  ["BeautifulSoup"]
      },
      packages=find_packages(exclude=('test')),
      
)
