#!/usr/bin/env python
import subprocess
import RPi.GPIO as GPIO
import time
from datetime import datetime
import serial
import os

#method to be invoked once stm32 requests us to read Serial
def checkUARTSerial(channel):
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print '['+ts+'] STM32 Event Detected!!'
  buff = serial.readline()
  buffSplit = buff.split("+")
  #our buff buffer may contain more than one message, iterate through them..
  for x in range(1, len(buffSplit)):
    msg = buffSplit[x]
    splitMsg  = msg.split("#")
    device = splitMsg[0]
    checkSum = splitMsg[7]
    if checkSum == 'csum':
      #if event comes from NRF24L01 network
      if device == 'N':
        event = splitMsg[1]
        nodeID = splitMsg[2]
        uniqueID = splitMsg[3]
        msgType = splitMsg[4]
        msg = splitMsg[5]
        analogMsg = splitMsg[6]
        print "Got event "+event+" nodeID "+nodeID+" uniqueID "+uniqueID+" msg type "+msgType+" msg "+msg+" float msg "+analogMsg
        #R for request from sensors to join network we return true if sensor is registered by user
        if event == 'R':
          os.system('/home/pi/Watchman/handleJoinRequest.py '+nodeID)
          pass
        #U for update, we update registeredSensors table alive column and last seen column if sensor is found to be responsive or dead
        elif event == 'U':
          os.system('/home/pi/Watchman/handleUpdateEvents.py '+nodeID+' '+msg)
          pass
        #V for events from vibration sensor
        elif event == 'V':
          pass
        #M for events from motion sensor
        elif event == 'M':
          pass
        pass
      #if event comes from SIM800L device
      elif device == 'G':
        pass

#check if script is already running
c = open("/home/pi/Watchman/checkEvents.txt","r")
status = c.read()
status = status.strip()
c.close()
if status == '1':
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] checkEvents already running!!'
  exit()

stm32Request = 16

#create serial interface object
serial = serial.Serial(
  port='/dev/ttyAMA0',
  baudrate=115200,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=5
)

#setup the GPIO Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(stm32Request, GPIO.IN, GPIO.PUD_DOWN)

#add event detection to pins
GPIO.add_event_detect(stm32Request, GPIO.RISING, checkUARTSerial, 10)

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+'] Check Events running..'

c = open("/home/pi/Watchman/checkEvents.txt","w+")
status = c.write('1')
c.close()
try:
  while(True):
    time.sleep(1)

except:
  GPIO.cleanup()
  c = open("/home/pi/Watchman/checkEvents.txt","w+")
  status = c.write('0')
  c.close()
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] Exiting..'

