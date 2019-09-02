#!/usr/bin/env python
import mysql.connector as mariadb
import MySQLdb
import subprocess
import time
from datetime import datetime

time = datetime.now()

mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
cursor = mariadb_connection.cursor()

try:
  cursor.execute("SELECT IP, sensorName, lastSeen, deviceType FROM registeredWifiSensors UNION SELECT IP, camName, lastSeen, deviceType FROM registeredIPCameras")
  result = cursor.fetchall()
  for row in result:
    ip = row[0]
    name = row[1]
    lastSeen = row[2]
    deviceType = row[3]
    timeDifference = time - lastSeen

    if timeDifference.total_seconds() > 130:
      msg = ip+'^'+name+'^'+deviceType+'^U^0^0'
      #print msg
      subprocess.call(['sudo','/home/pi/Watchman/mqtt/handleMqttSensorUpdates.py',msg])

  cursor.close()

except mariadb.Error as error:
  print("Error: {}".format(error))

mariadb_connection.close()

