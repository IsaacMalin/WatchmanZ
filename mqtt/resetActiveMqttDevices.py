#!/usr/bin/env python
import mysql.connector as mariadb
import MySQLdb
import subprocess
import time
from datetime import datetime
from ConfigParser import SafeConfigParser

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+'] Checking Active MQTT Devices..'
config = SafeConfigParser()
config.read('/home/pi/Watchman/sqldb/sqlCredentials.ini')

usr = config.get('credentials', 'username')
pswd = config.get('credentials', 'password')
db = config.get('credentials', 'database')

time = datetime.now()

mariadb_connection = mariadb.connect(user=usr, password=pswd,database=db)
cursor = mariadb_connection.cursor()

try:
  cursor.execute("SELECT IP, sensorName, lastSeen, deviceType FROM registeredWifiSensors UNION SELECT IP, camName, lastSeen, deviceType FROM registeredIPCameras")
  result = cursor.fetchall()
  for row in result:
    ip = row[0]
    name = row[1]
    lastSeen = row[2]
    deviceType = row[3]
    if lastSeen != None:
      timeDifference = time - lastSeen
    else:
      continue
    if timeDifference.total_seconds() > 130:
      msg = ip+'^'+name+'^'+deviceType+'^D^0^0'
      #print msg
      subprocess.call(['sudo','/home/pi/Watchman/mqtt/handleMqttSensorUpdates.py',msg])

  cursor.close()

except Exception as error:
  print("["+time.strftime('%d-%m-%Y %H:%M:%S')+"]Error: {}".format(error))
  exit()

mariadb_connection.close()

