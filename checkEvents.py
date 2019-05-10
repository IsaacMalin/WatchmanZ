#!/usr/bin/env python
import subprocess
import RPi.GPIO as GPIO
import time
from datetime import datetime
import serial

#method to be invoked once stm32 requests us to read Serial
def checkUARTSerial(channel):
  switchLed('red',1)
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
          switchLed('blue',1)
          subprocess.Popen(['sudo','/home/pi/Watchman/handleJoinRequest.py',nodeID])
          pass
        #U for update, we update registeredSensors table alive column and last seen column if sensor is found to be responsive or dead
        elif event == 'U':
          subprocess.Popen(['sudo','/home/pi/Watchman/handleUpdateEvents.py',nodeID,msg])
          pass
        #V for events from vibration sensor
        elif event == 'V':
          switchLed('blue',1)
          subprocess.Popen(['sudo','/home/pi/Watchman/handleAlertEvent.py',nodeID,event])
          pass
        #M for events from motion sensor
        elif event == 'M':
          switchLed('blue',1)
          subprocess.Popen(['sudo','/home/pi/Watchman/handleAlertEvent.py',nodeID,event])
          pass
        pass
      #if event comes from SIM800L device
      elif device == 'G':
        switchLed('green',1)
        pass
  switchLed('red',0)

def switchLed(led,state):
  if led == 'red':
    if state == 1:
      GPIO.output(redLed,GPIO.LOW)
    elif state == 0:
      GPIO.output(redLed,GPIO.HIGH)
    pass
  elif led == 'green':
    if state == 1:
      GPIO.output(greenLed,GPIO.LOW)
    elif state == 0:
      GPIO.output(greenLed,GPIO.HIGH)
    pass
  elif led == 'blue':
    if state == 1:
      GPIO.output(blueLed,GPIO.LOW)
    elif state == 0:
      GPIO.output(blueLed,GPIO.HIGH)
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
redLed = 11
greenLed = 13
blueLed = 15

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
GPIO.setup(redLed, GPIO.OUT, initial = 1)
GPIO.setup(greenLed, GPIO.OUT, initial = 1)
GPIO.setup(blueLed, GPIO.OUT, initial = 1)

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

