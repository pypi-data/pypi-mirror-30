from evtcantools.dbcparser import CANDatabase
import evtcantools.dbcparser
import errno
import os


MOST_RECENT = "IEC.dbc"
class DataBaseMaker(object):

    def __init__(self):
        pass

    @property
    def dbc_path(self):
        return os.path.join(os.path.dirname(__file__), 'dbcfiles')

    def file_path(self, filename):
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
