from utils.database_handle import DataBaseClient
from utils.serializer import serialPort
import aioschedule as schedule
from datetime import datetime
import asyncio
import serial
import time
import math

async def task(message):
      print(f"async task to record data on {message} interval")
      await asyncio.sleep(1)
      ser = serialPort()
      db  = DataBaseClient()

      record = {
            "soil_moisture": "get moisture",
            "temperature": "get temperature",
            "humidity": "get humidity",
            "co2": "get dioxide"
      }
      while True:
            for key, value in record.items():
                  
                  if type(value) is str:
                        ser.write(value.encode())
                        time.sleep(0.5)
                        value = ser.readline().decode("ascii")
                        print(f'{key}: {value}')
                        if value != '' and value != 'nan' :
                              value = float(value)
                              if not math.isnan(value):
                                    print(f'inserting {value} of key {key}')
                                    record[key] = value


                  if all(type(value) is float for value in record.values()):
                        record['date_time'] = datetime.now()
                        result = db.collection.insert_one(record)
                        print(f'record {result.inserted_id} was inserted')
                        ser.close
                        return
                  
def main():
      schedule.every().hour.at(':00').do(task, message='10 s')
      loop = asyncio.get_event_loop()
      while True:
            loop.run_until_complete(schedule.run_pending())
            time.sleep(0.1)

if __name__ == '__main__':
      main()

