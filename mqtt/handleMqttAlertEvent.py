#!/usr/bin/python
import sys
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

msg = sys.argv[1]
msgSplit = msg.split('^')

ip = msgSplit[0]
alertMsg = msgSplit[1]

print 'IP: '+ip+' reports msg: '+alertMsg

time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

mariadb_connection = mariadb.connect(user=usr, password=pswd,database=db)
cursor = mariadb_connection.cursor()
sendAlert = 0

try:
  cursor.execute("SELECT * FROM registeredWifiSensors WHERE IP = '"+str(ip)+"'")
  result = cursor.fetchall()
  for row in result:
    mediaOption = row[7]
    sendAlert = row[9]
    sendSms = row[10]
    vidLength = row[8]
    sensorName = row[1]
    camType = row[5]
    useCam = row[11]
    camIP = row[6]
  cursor.close()
except mariadb.Error as error:
  print("Error: {}".format(error))
  exit()

mariadb_connection.close()
ms = datetime.now().strftime("%H:%M:%S")
sensorMsg = sensorName+' ['+ip+'] reports '+alertMsg+' at '+ms
subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',str(ms)+' New alert from:','2'])
subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',str(sensorName),'3'])

if sendAlert == 1:
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  ipath = ' '
  vpath = ' '
  #send message to telegram user
  print 'Sending message to Telegram..'
  output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", sensorMsg, str(sendSms)])
  if useCam == 1:
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
        ipImgPath = '/home/pi/Pictures/IpCam/'
        ipImgName = 'Ip-Cam['+ts+'].jpg'
        ipath = ipImgPath+ipImgName
        #take image from pi-camera
        output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takeIpCamImg.sh", ipath, str(camIP)])
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
        output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takeUSB1CamVid.sh", vpath, str(vidLength)])
        pass
      elif camType == 'picam':
        piVidPath = '/home/pi/Videos/PiCam/'
        piVidName = 'Pi-Cam['+ts+'].mp4'
        vpath = piVidPath+piVidName
        #take video from pi-camera
        output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takePiCamVid.sh", vpath, str(vidLength*1000)])
        pass
      elif camType == 'ipcam':
        ipVidPath = '/home/pi/Videos/IpCam/'
        ipVidName = 'Ip-Cam['+ts+'].mp4'
        vpath = ipVidPath+ipVidName
        #take video from pi-camera
        output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takeIpCamVid.sh", vpath, str(vidLength) ,str(camIP)])
        pass
      #send video to telegram user
      print 'Sending video to Telegram..'
      output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendVid.py", vpath])
