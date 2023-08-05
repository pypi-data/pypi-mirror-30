import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup , find_packages


setup(name='EVT CAN Tools',
      version='0.1.0',
      description='Tools shared across software projects',
      url='https://bitbucket.org/evt/evt-can-tools',
      data_files = [],
      author='EVT RIT',
      author_email='EVT@RIT.EDU',
      packages=find_packages(),
      scripts= [],
      license='MIT',
      include_package_data=True,
      package_data={ '': ['*.txt', '*.rst']},
      zip_safe=False,
      entry_points ={

      })


BIN_PATH = '/usr/local/bin'
