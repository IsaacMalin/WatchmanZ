#!/usr/bin/python
import sys
import serial

sms = sys.argv[1]
print 'sending sms...'

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
msg = "+G^"+sms
serial.write(msg)
serial.close()
print "msg fowarded to STM32.."

