#!/usr/bin/env python
import paho.mqtt.client as mqtt #import the client1
import time
from datetime import datetime
import subprocess
############
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
########################################
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

try:
  broker_address="localhost"
  print("creating new instance")
  client = mqtt.Client("MasterSub") #create new instance
  client.on_message=on_message #attach function to callback
  print("connecting to broker")
  client.connect(broker_address) #connect to broker
  client.loop_start() #start the loop
  #subscribe to interesting topics..
  print("Subscribing to topic","sensorStatus","sensorAlert","sensorUpdates")
  client.subscribe("sensorStatus")
  client.subscribe("sensorAlert")
  client.subscribe("sensorUpdates")

  c = open("/home/pi/Watchman/mqtt/mqttSub.txt","w+")
  status = c.write('1')
  c.close()

  while(True):
    time.sleep(1)

except:
  c = open("/home/pi/Watchman/mqtt/mqttSub.txt","w+")
  status = c.write('0')
  c.close()
  client.loop_stop() #stop the loop
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] Exiting from script..'
