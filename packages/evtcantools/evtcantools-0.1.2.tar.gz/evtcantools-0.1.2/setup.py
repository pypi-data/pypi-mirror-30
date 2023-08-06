import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup , find_packages


long_description = """This package consists of tools shared across firware and software plateforms.
For dbc file creation use the dbcmaker module in order to fetch the most current EvtCan Revision or \
load from a given path  """


setup(name='evtcantools',
      version='0.1.2',
      description='Tools shared across EVT software projects',
      url='https://bitbucket.org/evt/evt-can-tools',
      data_files = [],
      author='EVT RIT',
      author_email='evt@rit.edu',
      long_description = long_description,
      packages=find_packages(),
      scripts= [],
      license='MIT',
      include_package_data=True,
      package_data={ '': ['*.txt', '*.rst', '*.dbc'], },
      zip_safe=False,
      entry_points ={

      })


BIN_PATH = '/usr/local/bin'
