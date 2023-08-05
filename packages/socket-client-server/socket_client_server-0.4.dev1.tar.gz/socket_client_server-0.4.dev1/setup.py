#!/bin/python

from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='socket_client_server',
      version='0.4.dev1',
      description='UNIX domain socket client and server classes',
      keywords='server client unix socket daemon',
      url='https://github.com/mbunse/socket_client_server',
      author='Moritz Bunse',
      author_email='mbunse@hotmail.com',
      license='MIT',
      packages=find_packages(exclude=['test']),
      install_requires=['future', 'six'],
      python_requires='>=2.7'
      )