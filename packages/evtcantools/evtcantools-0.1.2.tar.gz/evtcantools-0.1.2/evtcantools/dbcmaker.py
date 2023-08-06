"""
    Created:    03/20/2018
"""

from evtcantools.dbcparser import CANDatabase
import evtcantools.dbcparser
import errno
import os


MOST_RECENT = "IEC.dbc"
class DataBaseMaker(object):
    """
    Loads a given version of the dbc file either from the repository or a given file path
    """

    def __init__(self):
        pass

    @property
    def dbc_path(self):
        """ retrieves the dbcfile folder location relative to the install"""
        return os.path.join(os.path.dirname(__file__), 'dbcfiles')

    def file_path(self, filename):
        """returns a complete file path given a filename"""
        return os.path.join(self.dbc_path,filename)

    def retreive_file(self,version=None):
        if version is None:
            return self.file_path(MOST_RECENT)
        else:
            return self.file_path(version)

    def db_from_repo(self,version=MOST_RECENT):
        """
        creates a unloaded database from the evtcantools repository
        """
        return CANDatabase(self.retreive_file(version=version))

    def db_from_path(self,path):
        """
        createas an unloaded db given a filepath
        """
        if os.path.exists(path):
            return CANDatabase(path)
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
