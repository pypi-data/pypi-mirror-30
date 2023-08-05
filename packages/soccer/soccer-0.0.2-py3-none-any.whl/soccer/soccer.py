""" Central class for the soccer data api. """
from soccer.data_connectors import FDOConnector, SQLiteConnector

class Soccer(object):
    """
    Central class for the soccer data api.
    """
    def __init__(self, fd_apikey=None, db_path=None):
        self.fdo = FDOConnector(fd_apikey)
        self.db = SQLiteConnector(db_path)
        season = self.get_current_season()

    def get_current_season(self):
        self.fdo.get_current_season()
        
