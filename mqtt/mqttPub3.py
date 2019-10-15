#!/usr/bin/python3
import paho.mqtt.client as mqtt
import sys

#get arguments
topic = sys.argv[1]
msg = sys.argv[2]

try:
  broker_address="localhost"
  client = mqtt.Client("MasterPub")
  client.connect(broker_address)
  client.publish(topic,msg)
  print('Published msg: '+msg+' to topic: '+topic)
except:
  print('Publish msg: '+msg+' to topic: '+topic+' failed!')

