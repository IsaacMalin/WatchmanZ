#!/usr/bin/env python
import mysql.connector as mariadb
import MySQLdb
import subprocess
import time as t
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
#sleep to allow other scripts to update their status first before checking for dead sensors i.e if both scripts are triggered at the same time
t.sleep(5)

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
    if timeDifference.total_seconds() > 240:
      msg = ip+'^'+name+'^'+deviceType+'^D^0^0'
      #print msg
      subprocess.call(['sudo','/home/pi/Watchman/mqtt/handleMqttSensorUpdates.py',msg])

  cursor.close()

except Exception as error:
  print("["+time.strftime('%d-%m-%Y %H:%M:%S')+"]Error: {}".format(error))
  exit()

mariadb_connection.close()

