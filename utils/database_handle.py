__package__ = 'utils'

from bson import binary
from pymongo import MongoClient

class DataBaseClient:
      def __init__(self, host:str = '127.0.0.1', port:int = 27017, db:str ='flora_data', collection:str = 'telemetry'):
            self.host       = host
            self.port       = port
            self.db         = db 
            self.client     = MongoClient(self.host , self.port)
            self.database   = self.client[self.db]
            if collection == 'telemetry':
                  self.collection = self.database.telemetry
            if collection == 'images':
                  self.collection = self.database.images

      def get_all_records(self):
            return self.collection

      def get_record(self):
            pass

      def insert_record(self):
            pass
