#!/usr/bin/python
import sys
import os
import mysql.connector as mariadb
import MySQLdb
import time
from datetime import datetime

nodeID = sys.argv[1]
state = sys.argv[2]
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
cursor = mariadb_connection.cursor()

try:
  cursor.execute("UPDATE registeredSensors SET active = '%s', lastSeen = '%s' WHERE nodeID = '%s'"%(state,time,nodeID))
  cursor.close()
except mariadb.Error as error:
  print("Error: {}".format(error))

mariadb_connection.commit()
mariadb_connection.close()

