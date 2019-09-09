#!/usr/bin/python
import sys
import os
import mysql.connector as mariadb
import MySQLdb
import subprocess
import time
from datetime import datetime
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('/home/pi/Watchman/sqldb/sqlCredentials.ini')

usr = config.get('credentials', 'username')
pswd = config.get('credentials', 'password')
db = config.get('credentials', 'database')

nodeID = sys.argv[1]
state = sys.argv[2]
batt = sys.argv[3]
stateInt = int(state)
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
previousState = 1

mariadb_connection = mariadb.connect(user=usr, password=pswd,database=db)
cursor = mariadb_connection.cursor()
cursor2 = mariadb_connection.cursor()

try:
  cursor2.execute("SELECT * FROM registeredNRFSensors WHERE nodeID = "+nodeID)
  result = cursor2.fetchall()
  for row in result:
    previousState = row[4]
    sensorName = row[1]
    localID = row[2]
    previousBatt = row[14]
  cursor2.close()

except mariadb.Error as error:
  previousState = 0
  print("Error: {}".format(error))

if state == '0':
  batt = previousBatt

try:
  cursor.execute("UPDATE registeredNRFSensors SET active = '%s', lastSeen = '%s', batt = '%s' WHERE nodeID = '%s'"%(state,time,batt,nodeID))
  cursor.close()
except Error:
  print("Error: {}".format(error))

mariadb_connection.commit()
mariadb_connection.close()

if previousState != stateInt:
  try:
    if stateInt == 1:
      updateMsg = sensorName+' ['+localID+'] is now active.'
    else:
      updateMsg = sensorName+' ['+localID+'] has gone offline.'
    print updateMsg
    output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", updateMsg, '0'])
  except:
    print time+' unable to send update msg to Telegram.'

