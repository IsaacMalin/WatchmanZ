#!/usr/bin/env python
import paho.mqtt.client as mqtt #import the client1
import time
import sys
from datetime import datetime
import subprocess
import RPi.GPIO as GPIO
from ConfigParser import SafeConfigParser

def exitScript(e = 'Closing mqttSub.py'):
  print 'Error: {}'.format(e)
  c = open("/home/pi/Watchman/mqtt/mqttSub.txt","w+")
  status = c.write('0')
  c.close()
  client.loop_stop() #stop the loop
  GPIO.cleanup()
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] Exiting from script..'
  sys.exit()
################################################################################################
def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    topic = message.topic
    qos = message.qos
    retainFlag = message.retain
    print("message received " ,msg)
    print("message topic=",topic)
    print("message qos=",qos)
    print("message retain flag=",retainFlag)
    if topic == 'sensorAlert':
      subprocess.Popen(['sudo','/home/pi/Watchman/mqtt/handleMqttAlertEvent.py',msg])
      pass
    elif topic == 'sensorUpdates':
      subprocess.Popen(['sudo','/home/pi/Watchman/mqtt/handleMqttSensorUpdates.py',msg])
      pass
    elif topic == 'sensorStatus':
      subprocess.Popen(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',msg,'0'])
      pass
    elif topic == 'powerStatus':
      subprocess.Popen(['sudo','/home/pi/Watchman/mqtt/handlePowerUpdate.py',msg])
################################################################################################
def port1Triggered(channel):
  print "Port 1 Triggered!!"
  time.sleep(0.002)
  timing1 = GPIO.input(port1)
  time.sleep(0.005)
  timing2 = GPIO.input(port1)
  time.sleep(0.005)
  timing3 = GPIO.input(port1)
  time.sleep(0.005)
  timing4 = GPIO.input(port1)
  time.sleep(0.005)
  timing5 = GPIO.input(port1)
  time.sleep(0.005)
  timing6 = GPIO.input(port1)
  time.sleep(0.005)
  timing7 = GPIO.input(port1)
  time.sleep(0.005)
  timing8 = GPIO.input(port1)
  time.sleep(0.005)
  timing9 = GPIO.input(port1)

  if (timing4 == 0 and timing5 == 1) or (timing1 == 0 and timing2 == 0 and timing3 == 0 and timing4 == 0 and timing5 == 0):
    try:
      msg =  str(ip)+'^1^'+str(timing1)+str(timing2)+str(timing3)+'^'+str(timing6)+str(timing7)+str(timing8)+str(timing9)
      print msg
      subprocess.Popen(['sudo','/home/pi/Watchman/mqtt/handleMqttAlertEvent.py',msg])
    except Exception as e:
      print 'Error: {}'.format(e)
def port2Triggered(channel):
  print "Port 2 Triggered!!"
  time.sleep(0.002)
  timing1 = GPIO.input(port2)
  time.sleep(0.005)
  timing2 = GPIO.input(port2)
  time.sleep(0.005)
  timing3 = GPIO.input(port2)
  time.sleep(0.005)
  timing4 = GPIO.input(port2)
  time.sleep(0.005)
  timing5 = GPIO.input(port2)
  time.sleep(0.005)
  timing6 = GPIO.input(port2)
  time.sleep(0.005)
  timing7 = GPIO.input(port2)
  time.sleep(0.005)
  timing8 = GPIO.input(port2)
  time.sleep(0.005)
  timing9 = GPIO.input(port2)

  if (timing4 == 0 and timing5 == 1) or (timing1 == 0 and timing2 == 0 and timing3 == 0 and timing4 == 0 and timing5 == 0):
    try:
      msg =  str(ip)+'^2^'+str(timing1)+str(timing2)+str(timing3)+'^'+str(timing6)+str(timing7)+str(timing8)+str(timing9)
      print msg
      subprocess.Popen(['sudo','/home/pi/Watchman/mqtt/handleMqttAlertEvent.py',msg])
    except Exception as e:
      print 'Error: {}'.format(e)
def port3Triggered(channel):
  print "Port 3 Triggered!!"
  time.sleep(0.002)
  timing1 = GPIO.input(port3)
  time.sleep(0.005)
  timing2 = GPIO.input(port3)
  time.sleep(0.005)
  timing3 = GPIO.input(port3)
  time.sleep(0.005)
  timing4 = GPIO.input(port3)
  time.sleep(0.005)
  timing5 = GPIO.input(port3)
  time.sleep(0.005)
  timing6 = GPIO.input(port3)
  time.sleep(0.005)
  timing7 = GPIO.input(port3)
  time.sleep(0.005)
  timing8 = GPIO.input(port3)
  time.sleep(0.005)
  timing9 = GPIO.input(port3)

  if (timing4 == 0 and timing5 == 1) or (timing1 == 0 and timing2 == 0 and timing3 == 0 and timing4 == 0 and timing5 == 0):
    try:
      msg =  str(ip)+'^3^'+str(timing1)+str(timing2)+str(timing3)+'^'+str(timing6)+str(timing7)+str(timing8)+str(timing9)
      print msg
      subprocess.Popen(['sudo','/home/pi/Watchman/mqtt/handleMqttAlertEvent.py',msg])
    except Exception as e:
      print 'Error: {}'.format(e)

################################################################################################
ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'
print("Starting mqtt sub engine..")
#check if script is already running
c = open("/home/pi/Watchman/mqtt/mqttSub.txt","r")
status = c.read()
status = status.strip()
c.close()
if status == '1':
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] mqttSub already running!!'
  exit()

port1 = 11
port2 = 13
port3 = 15

ip = ''
try:
  config = SafeConfigParser()
  config.read('/home/pi/Watchman/WatchmanConfig.ini')
  ip = config.get('ConfigVariables', 'staticip')
except Exception as e:
  print 'iniError: {}'.format(e)

try:
  broker_address="localhost"
  print("creating new instance")
  client = mqtt.Client("MasterSub") #create new instance
  client.on_message=on_message #attach function to callback
  print("connecting to broker")
  client.connect(broker_address) #connect to broker
  client.loop_start() #start the loop
  #subscribe to interesting topics..
  print("Subscribing to topic","sensorStatus","sensorAlert","sensorUpdates","powerStatus")
  client.subscribe("sensorStatus")
  client.subscribe("sensorAlert")
  client.subscribe("sensorUpdates")
  client.subscribe("powerStatus")

  c = open("/home/pi/Watchman/mqtt/mqttSub.txt","w+")
  status = c.write('1')
  c.close()

  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(port1, GPIO.IN, GPIO.PUD_DOWN)
  GPIO.setup(port2, GPIO.IN, GPIO.PUD_DOWN)
  GPIO.setup(port3, GPIO.IN, GPIO.PUD_DOWN)

  GPIO.add_event_detect(port1, GPIO.FALLING, port1Triggered, 5000)
  GPIO.add_event_detect(port2, GPIO.FALLING, port2Triggered, 5000)
  GPIO.add_event_detect(port3, GPIO.FALLING, port3Triggered, 5000)

except Exception as e:
  exitScript(e)

try:
  while(True):
    time.sleep(1)

except:
  exitScript()
