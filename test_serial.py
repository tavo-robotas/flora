import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

while True:
      i = input("enter cmd: ").strip()

      if i == "done":
            print("finished")
            break
      print(time.perf_counter())
      ser.write(i.encode())
      time.sleep(0.5)
      print(ser.readline().decode("ascii"))
      print(time.perf_counter())

ser.close
