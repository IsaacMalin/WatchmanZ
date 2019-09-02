#!/usr/bin/env python
import sys
import mysql.connector as mariadb
import MySQLdb
import subprocess
import time
from datetime import datetime

msg = sys.argv[1]
msgSplit = msg.split('^')

ip = msgSplit[0]
name = msgSplit[1]
deviceType = msgSplit[2]
event = msgSplit[3]
state = msgSplit[4]
stateInt = int(state)
battLevel = msgSplit[5]
#print 'IP: '+ip+' Name: '+name+' Device_Type: '+deviceType+' Event: '+event+' State: '+state+' Level: '+battLevel

time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
previousState = 1

mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
cursor = mariadb_connection.cursor()
cursor2 = mariadb_connection.cursor()

try:
  if deviceType == 'S':
    cursor2.execute("SELECT * FROM registeredWifiSensors WHERE IP = \'"+ip+"\'")
    result = cursor2.fetchall()
    for row in result:
      previousState = row[2]
      sensorName = row[1]
      previousBatt = row[12]
  elif deviceType == 'C':
    cursor2.execute("SELECT * FROM registeredIPCameras WHERE IP = \'"+ip+"\'")
    result = cursor2.fetchall()
    for row in result:
      previousState = row[2]
      sensorName = row[1]
      previousBatt = row[6]
  else:
    cursor2.close()
    mariadb_connection.close()
    exit()
  cursor2.close()

except mariadb.Error as error:
  previousState = 0
  print("Error: {}".format(error))

try:
  if state == '0':
    battLevel = previousBatt
except:
  print 'IP Address '+ip+' did not match anything'
  exit()

try:
  if deviceType == 'S':
    cursor.execute("UPDATE registeredWifiSensors SET active = '%s', lastSeen = '%s', batt = '%s' WHERE IP = '%s'"%(state,time,battLevel,ip))
  elif deviceType == 'C':
    cursor.execute("UPDATE registeredIPCameras SET active = '%s', lastSeen = '%s', batt = '%s' WHERE IP = '%s'"%(state,time,battLevel,ip))
  cursor.close()
except Error:
  print("Error: {}".format(error))

mariadb_connection.commit()
mariadb_connection.close()

if previousState != stateInt:
  try:
    if stateInt == 1:
      updateMsg = sensorName+' ['+ip+'] is now active.'
    else:
      updateMsg = sensorName+' ['+ip+'] has gone offline.'
    print updateMsg
    output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", updateMsg, '0'])
  except:
    print time+' unable to send update msg to Telegram.'

