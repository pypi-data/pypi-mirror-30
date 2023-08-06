# -*- coding: utf-8 -*-
""" Setup py for futura ai

Todo:
    * Separate version from here

"""

from setuptools import setup, find_packages

VERSION = '0.0.11'


setup(name='futuraAiToolbox',
      version=VERSION,
      description='Python based toolbox for futuraAi',
      url='http://futura.ai',
      download_url='https://gitlab.com/futura.ai/genesisrepo/repository/master/archive.zip',
      author='Tanmay',
      author_email='tanmay@futura.ai',
      license='MIT',
      packages= find_packages(), #['futuraaiToolbox'],
      include_package_data=True,

      install_requires=[
          'backports.functools-lru-cache>=1.5',
          'cycler>=0.10.0',
          'kiwisolver>=1.0.1',
          'matplotlib>=2.2.2',
          'numpy>=1.14.2',
          'pandas>=0.22.0',
          'pyparsing>=2.2.0',
          'python-dateutil>=2.7.2',
          'pytz>=2018.3',
          'six>=1.11.0',
          'subprocess32>=3.2.7'
          ],

      zip_safe=False,
     )
