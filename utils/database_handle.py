__package__ = 'utils'

from pymongo import MongoClient

class DataBaseClient:
      def __init__(self, host:str = '127.0.0.1', port:int = 27017, db:str ='flora_data' ):
            self.host       = host
            self.port       = port
            self.db         = db 

            self.client     = MongoClient(self.host , self.port)
            self.database   = self.client[self.db]
            self.collection = self.database.telemetry

      def get_all_records(self):
            return self.collection

      def get_record(self):
            pass

      def insert_record(self):
            pass