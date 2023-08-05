#!/usr/bin/env python

from setuptools import setup


setup(name='python-bittrex-aio',
      version='0.0.1',
      url="https://github.com/BlockHub/python-bittrex-aio",
      packages=['aiobittrex'],
      modules=['aiobittrex'],
      install_requires=['aiohttp', 'aiodns', 'async-timeout', 'cchardet'],
      description='Asynchronous python bindings for bittrex API.',
      author='Karel L. Kubat',
      author_email='karel@blockhub.nl',
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Operating System :: OS Independent',
          'Development Status :: 3 - Alpha',
          'Topic :: Office/Business :: Financial',
      ])
