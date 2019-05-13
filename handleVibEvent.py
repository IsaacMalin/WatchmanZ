#!/usr/bin/env python
import sys
import subprocess
import RPi.GPIO as GPIO
import time
from datetime import datetime
import mysql.connector as mariadb
import MySQLdb

blueLed = 15
GPIO.setmode(GPIO.BOARD)
GPIO.setup(blueLed, GPIO.OUT, initial = 0)
nodeID = sys.argv[1]
event = sys.argv[2]
authorizeVibMsg = 0
sensorMsg = ' '

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

if event == 'V':
  print '['+ts+'] Vibration detected!!'
elif event == 'M':
  print '['+ts+'] Motion detected!!'
else:
  print '['+ts+'] Sensor alert detected!!'

mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
cursor = mariadb_connection.cursor()

try:
  cursor.execute("SELECT * FROM registeredSensors WHERE nodeID = "+nodeID)
  result = cursor.fetchall()
  for row in result:
    mediaOption = row[9]
    authorizeVibMsg = row[11]
    vidLength = row[10]
    localID = row[2]
    sensorName = row[1]
    camType = row[7]
  cursor.close()
except mariadb.Error as error:
  print("Error: {}".format(error))

mariadb_connection.close()

if authorizeVibMsg == 1:
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  ms = datetime.now().strftime("%H:%M:%S")
  if event == 'V':
    sensorMsg = sensorName+' ['+localID+'] reports vibration detected at '+ms
    pass
  elif event == 'M':
    sensorMsg = sensorName+' ['+localID+'] reports motion detected at '+ms
    pass
  else:
    sensorMsg = sensorName+' ['+localID+'] was triggered at '+ms
  ipath = ' '
  vpath = ' '
  #send message to telegram user
  print 'Sending message to Telegram..'
  output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", VibSensorMsg])
  if mediaOption == 'i':
    if camType == 'usbcam':
      imgPath = '/home/pi/Pictures/USB1Cam/'
      imgName = 'USB1Cam['+ts+'].jpg'
      ipath = imgPath+imgName
      #take image from usb1-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takeUSB1CamImg.sh", ipath])
      pass
    elif camType == 'picam':
      piImgPath = '/home/pi/Pictures/PiCam/'
      piImgName = 'Pi-Cam['+ts+'].jpg'
      ipath = piImgPath+piImgName
      #take image from pi-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takePiCamImg.sh", ipath])
      pass
    elif camType == 'ipcam':

      pass
    #send image to telegram user
    print 'Sending image to Telegram..'
    output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendPic.py", ipath])
  if mediaOption == 'v':
    if camType == 'usbcam':
      vidPath = '/home/pi/Videos/USB1Cam/'
      vidName = 'USB1Cam['+ts+'].avi'
      vpath = vidPath+vidName
      #take video from usb1-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takeUSB1CamVid.sh", vpath, vidLength])
      pass
    elif camType == 'picam':
      piVidPath = '/home/pi/Videos/PiCam/'
      piVidName = 'Pi-Cam['+ts+'].mp4'
      vpath = piVidPath+piVidName
      #take video from pi-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takePiCamVid.sh", vpath, vidLength*1000])
      pass
    elif camType == 'ipcam':

      pass
    #send video to telegram user
    print 'Sending video to Telegram..'
    output = subprocess.call(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendVid.py", vpath])

  #GPIO.output(switchIR, GPIO.LOW)
GPIO.output(blueLed,GPIO.LOW)
GPIO.cleanup()
