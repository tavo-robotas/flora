from utils.database_handle import DataBaseClient
from utils.serializer import serialPort
import aioschedule as schedule
from datetime import datetime
import asyncio
import time

def cmd_rcv(port, msg):
      #print(f'msg: {msg}')
      payload = msg.encode()
      #print(f'payload: {payload}')
      port.flush()
      port.writer(payload)
      val = port.reader()
      return val

async def task(message):
      print(f"async task to recorde data on {message} interval")
      asyncio.sleep(1)
      ser = serialPort()
      db  = DataBaseClient()
      
      ## TBD:
      ## stupid hack but it works while i will find out 
      ## the problem with timeout response form serial port
      date_time   = datetime.now()
      temperature = cmd_rcv(ser, "get temperature")
      temperature = cmd_rcv(ser, "get temperature")
      humidity    = cmd_rcv(ser, "get humidity")
      co2         = cmd_rcv(ser, "get dioxide")
      moisture    = cmd_rcv(ser, "get moisture") 
      moisture    = cmd_rcv(ser, "get moisture")  
 

      record = {
            "date_time"    : date_time,
            "soilmoisture" : int(moisture)/4,
            "temperature"  : float(temperature),
            "humidity"     : float(humidity),
            "co2"          : int(co2)

      }

      result = db.collection.insert_one(record)
      print(f'record {result.inserted_id} was inserted')
      ser.close

def main():
      schedule.every().hour.do(task, message='1h')
      loop = asyncio.get_event_loop()
      while True:
            loop.run_until_complete(schedule.run_pending())
            time.sleep(0.1)

if __name__ == '__main__':
      main()