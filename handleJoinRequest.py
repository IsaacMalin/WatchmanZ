#!/usr/bin/python
import sys
import os
import mysql.connector as mariadb
import MySQLdb
import RPi.GPIO as GPIO
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('/home/pi/Watchman/sqldb/sqlCredentials.ini')

usr = config.get('credentials', 'username')
pswd = config.get('credentials', 'password')
db = config.get('credentials', 'database')

blueLed = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(blueLed, GPIO.OUT, initial = 0)
nodeID = sys.argv[1]
uniqueID = 0
mariadb_connection = mariadb.connect(user=usr, password=pswd,database=db)
cursor = mariadb_connection.cursor()

try:
  cursor.execute("SELECT * FROM registeredNRFSensors WHERE nodeID = "+nodeID)
  result = cursor.fetchall()
  for row in result:
    uniqueID = row[3]
  cursor.close()
  os.system('sudo /home/pi/Watchman/sendToSTM32.py N '+str(uniqueID)+' '+str(nodeID)+' R 0 0')
except mariadb.Error as error:
  print("Error: {}".format(error))

mariadb_connection.close()
GPIO.output(blueLed,GPIO.LOW)
GPIO.cleanup()
