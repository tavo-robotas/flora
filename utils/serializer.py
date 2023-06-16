import serial
import time


class serialPort():
      def __init__(self, port:str = '/dev/ttyUSB0', baudrate:int=9600, timeout = 1):
            self.port = port 
            self.baudrate = baudrate
            self.timeout  = timeout 
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            
          
      def flush(self):
            self.ser.flush()

      def reader(self):
            val = self.ser.readline().decode("ascii")
            return val

      # def read(self):
      #       val = self.ser.readline()
      #       if val: 
      #             string = val.decode("ascii")  
      #             num = int(string) 
      #             print(num)
      #             return num
            
      
      def close(self):
            self.ser.close()

      def writer(self, payload):
            #print(f'payload from writer: {payload}')
            try:
                  self.ser.write(payload)
                  time.sleep(0.05)
            except ser.SerialException as e:
                  print(f"Error: Serial communication failed. {str(e)}")
          
