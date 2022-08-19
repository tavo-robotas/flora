from datetime import datetime
import plotly.express as px
import pandas as pd
import pymongo
import random


host         = '127.0.0.1'
port         =  27017
databasename = 'flora_data'


client     = pymongo.MongoClient(host, port)
database   = client[databasename]
collection = database.telemetry

dates = pd.date_range(end = datetime.today(), periods = 100).to_pydatetime().tolist()

def generate_data():
      for i in range(5):
            record = {
                  "date_time"    : dates[i],
                  "soilmoisture" : random.randint(500, 1000),
                  "temperature"  : round(random.normalvariate(25, 5),2),
                  "humidity"     : round(random.uniform(50.0, 100.0),2),
                  "co2"          : round(random.uniform(400.0, 600.0),2)
            }

            result = collection.insert_one(record)
            print(f'record {i} of 500 inserted as {result.inserted_id}')
generate_data()
print('all good')