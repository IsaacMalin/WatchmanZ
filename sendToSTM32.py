#!/usr/bin/python
import serial
import time
import sys

#get arguments
device = sys.argv[1]
data = sys.argv[2]
arg1 = sys.argv[3]
arg2 = sys.argv[4]
arg3 = sys.argv[5]
arg4 = sys.argv[6]

#create serial object
serial = serial.Serial(
  port='/dev/ttyAMA0',
  baudrate = 115200,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=5
)

#construct message
msg = "+"+device+"#"+data+"#"+arg1+"#"+arg2+"#"+arg3+"#"+arg4
print msg+" sent to STM32"

serial.write(msg);
