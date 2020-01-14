#!/usr/bin/env python
import os
import time
import sys
from datetime import datetime
import subprocess
import telepot
import socket
from ConfigParser import SafeConfigParser


tok = ''
try:
  config = SafeConfigParser()
  config.read('/home/pi/Watchman/WatchmanConfig.ini')
  tok = config.get('ConfigVariables', 'token')
except:
  print 'Error reading telegram bot config'
  sys.exit()

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'

imgpath = ['/home/pi/ftp/files/Pics','/home/pi/Pictures/PiCam','/home/pi/Pictures/USB1Cam']
vidpath = ['/home/pi/ftp/files/Vids','/home/pi/Videos/PiCam','/home/pi/Videos/USB1Cam']

def checkInternet(hostname):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80))
    s.close()
    return True
  except Exception as e:
     pass
  return False

REMOTE_SERVER = 'www.google.com'

if checkInternet(REMOTE_SERVER):
  print 'Uploading files to telegram'

  try:
    bot = telepot.Bot(tok)
    data = bot.getMe()
    for p in imgpath:
      for f in os.listdir(p):
          f = os.path.join(p, f)
          if os.path.isfile(f):
            print 'uploading image file : '+f
            output = subprocess.check_output(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendPic.py',f])
            #if 'sent' in output:
            #  os.remove(f)

    for p in vidpath:
      for f in os.listdir(p):
          f = os.path.join(p, f)
          if os.path.isfile(f):
            print 'uploading video file : '+f
            output = subprocess.check_output(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendVid.py',f])
            #if 'sent' in output:
            #  os.remove(f)

    print 'Finished uploading files..'
  except:
    print 'Connection to telegram failed!!'
else:
  print 'No internet, upload script terminated !'
