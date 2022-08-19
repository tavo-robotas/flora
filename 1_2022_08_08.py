import serial
import time
import datetime
from pymongo import MongoClient

serial_port          = '/dev/ttyUSB0'
mongodb_host         = '127.0.0.1'
mongodb_db           = 'flora_state'


ser = serial.Serial(serial_port, 9600, timeout=0)
cln = MongoClient(mongodb_host, 27017)

db = cln[mongodb_db]
collection = db['data_log']

interval = 10

while True:
      try:
            temparature = ser.readline().rstrip()

            if temparature:
                  temperature_celsius = float(temparature)
                  document_id         = collection.insert_one({
                        'temperature': temperature_celsius,
                        'datetime'   : datetime.datetime.now(),
                  }).inserted_id

                  #print(f'{str(document_id)} : {str(temperature_celsius)}')
            
      except serial.SerialTimeoutException:
            print('error: could not read temperature value from unit')
      except ValueError:
            print('error: could not convert temperature to float')
      finally:
            time.sleep(interval)