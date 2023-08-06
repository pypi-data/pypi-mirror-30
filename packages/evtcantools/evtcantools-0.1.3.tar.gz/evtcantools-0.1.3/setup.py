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
      version='0.1.3',
      description='Tools shared across EVT software projects',
      url='https://bitbucket.org/evt/evt-can-tools',
      author='EVT RIT',
      author_email='evt@rit.edu',
      long_description = long_description,
      packages=['evtcantools',],
      license='MIT',
      package_data={ 'evtcantools': ['dbcfolder/*.dbc'] },
      zip_safe=False,
      entry_points ={
      })
