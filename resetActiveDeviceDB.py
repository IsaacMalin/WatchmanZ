#!/usr/bin/python
import sys
import os
import mysql.connector as mariadb
import MySQLdb

mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
cursor = mariadb_connection.cursor()

try:
  cursor.execute("UPDATE registeredNRFSensors SET active = '0'")
  cursor.close()
except mariadb.Error as error:
  print("Error: {}".format(error))

mariadb_connection.commit()
mariadb_connection.close()
