#!/usr/bin/env python
import subprocess
import RPi.GPIO as GPIO
import time
from datetime import datetime
import serial
import socket

#method to be invoked once stm32 requests us to read Serial
def checkUARTSerial(channel):
  switchLed('red',1)
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print '['+ts+'] STM32 Event Detected!!'
  buff = serial.readline()
  serial.flushInput()
  print buff
  buffSplit = buff.split("+")
  #our buff buffer may contain more than one message, iterate through them..
  for x in range(1, len(buffSplit)):
    msg = buffSplit[x]
    splitMsg  = msg.split("^")
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
        #r for resetting active devices database
        elif event == 'r':
          subprocess.Popen(['sudo','/home/pi/Watchman/resetActiveDeviceDB.py'])
          pass
        #U for update, we update registeredSensors table alive column and last seen column if sensor is found to be responsive or dead
        elif event == 'U':
          subprocess.Popen(['sudo','/home/pi/Watchman/handleUpdateEvents.py',nodeID,msg])
          pass
        #V for events from vibration sensor
        elif event == 'A':
          switchLed('blue',1)
          subprocess.Popen(['sudo','/home/pi/Watchman/handleAlertEvent.py',nodeID,msgType])
          pass
        pass
      #if event comes from SIM800L device
      elif device == 'G':
        switchLed('green',1)
        event = splitMsg[1]
        msg = splitMsg[5]
        subprocess.call(['sudo','/home/pi/Watchman/handleSim800lTEvent.py',event,msg])
        pass
  switchLed('red',0)

#method to play audio messages to admin if we call the admin
def playMsgIfCallingUser(channel):
  print 'Admin has been called, now playing pending message'
  c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","r")
  msg = c.read()
  immediateMsg = 'You have no new message, '
  if len(msg) > 2:
    immediateMsg = 'You have a message, '+msg+', '
  c.close()
  lastMsg = 'Thank you for your time and have a nice day.'
  subprocess.Popen(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/secondCallingMsg.wav',immediateMsg+lastMsg])
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/firstCallingMsg.wav'])
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/secondCallingMsg.wav'])
  #Clear text file once the message has been played to user
  c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","w")
  c.write('0')
  c.close()

#method to play audio message if admin calls us
def playMsgIfUserCalled(channel):
  print 'Admin called us, now playing status and pending messages'
  #check if we have pending messages..
  c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","r")
  msg = c.read()
  pendingMsg = 'You have no pending messages, '
  if len(msg) > 2:
    pendingMsg = 'You have some pending messages. '+msg
  c.close()

  #check the battery status and if we are running on mains power or battery power
  b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","r")
  msg = b.read()
  battMsg = 'Power source and battery status is unknown, '
  if len(msg) > 4:
    splitMsg = msg.split('#')
    source = splitMsg[0]
    level = splitMsg[1]
    sourceMsg = 'The system is running on mains power. '
    if(source == '1'):
      sourceMsg = 'The system is running on battery power. '
    battMsg = sourceMsg+'The battery level is, '+level+'.  '
  b.close()

  #play first msg as we process other commands..
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/firstCalledMsg.wav'])

  #check if we are connected to the internet
  netMsg = 'Ping to google servers failed, there is no connection to the internet. You will not receive sensor messages via telegram, until internet connection is restored. '
  if(checkInternet(REMOTE_SERVER)):
    netMsg = 'Internet connection is available, I will be sending all sensor messages, to you via telegram. '

  lastMsg = 'Thank you for your time and have a nice day.'

  subprocess.call(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/secondCalledMsg.wav',pendingMsg+battMsg+netMsg+lastMsg])
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/secondCalledMsg.wav'])

  #Clear text file once the message has been played to user
  c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","w")
  c.write('0')
  c.close()

def checkInternet(hostname):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80))
    s.close()
    return True
  except:
     pass
  return False

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
outCallPin = 22
inCallPin = 37
REMOTE_SERVER = 'www.google.com'

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
GPIO.setup(outCallPin, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(inCallPin, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(redLed, GPIO.OUT, initial = 1)
GPIO.setup(greenLed, GPIO.OUT, initial = 1)
GPIO.setup(blueLed, GPIO.OUT, initial = 1)

#add event detection to pins
GPIO.add_event_detect(stm32Request, GPIO.RISING, checkUARTSerial, 10)
GPIO.add_event_detect(outCallPin, GPIO.RISING, playMsgIfCallingUser, 5000)
GPIO.add_event_detect(inCallPin, GPIO.RISING, playMsgIfUserCalled, 5000)

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+'] Check Events running..'

c = open("/home/pi/Watchman/checkEvents.txt","w+")
status = c.write('1')
c.close()
try:
  while(True):
    time.sleep(1)

except:
  serial.close()
  GPIO.cleanup()
  c = open("/home/pi/Watchman/checkEvents.txt","w+")
  status = c.write('0')
  c.close()
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] Exiting..'

