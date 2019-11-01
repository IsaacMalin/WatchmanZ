#!/usr/bin/python
import subprocess
import sys
from ConfigParser import SafeConfigParser

ip = ''
name = 'Gateway Hub'
batt = ''

try:
  config = SafeConfigParser()
  config.read('/home/pi/Watchman/WatchmanConfig.ini')
  ip = config.get('ConfigVariables', 'staticip')
except Exception as e:
  print 'iniError: {}'.format(e)
  sys.exit()

try:
  b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","r")
  msg = b.read()
  if len(msg) > 4:
    splitMsg = msg.split('#')
    level = splitMsg[1]
    batt = level.replace('%','')
  else:
    batt = 0
  b.close()
except:
  b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","w+")
  b.write(' ')
  b.close()
  sys.exit()

msg = str(ip)+'^'+name+'^S^U^1^'+str(batt)

subprocess.call(["/home/pi/Watchman/mqtt/handleMqttSensorUpdates.py",msg])


