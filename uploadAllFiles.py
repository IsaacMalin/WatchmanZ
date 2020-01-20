#!/usr/bin/env python
import os
import time
import sys
from datetime import datetime
import subprocess
import telepot
import socket
from ConfigParser import SafeConfigParser


ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'

#check if this script is already running
status = '1'
try:
  c = open("/home/pi/Watchman/uploadAllFiles.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  err = 'Error: {}'.format(e)
  print err
  if 'No such file' in err:
    c = open("/home/pi/Watchman/uploadAllFiles.txt","w+")
    status = c.write('0')
    c.close()
  sys.exit()
if status == '1':
  print'already uploading files..'
  sys.exit()
else:
  c = open("/home/pi/Watchman/uploadAllFiles.txt","w")
  status = c.write('1')
  c.close()

def exitScript(e='Closing uploadAllFiles.py script!'):
  print 'Exit status: {}'.format(e)
  c = open("/home/pi/Watchman/uploadAllFiles.txt","w")
  status = c.write('0')
  c.close()
  sys.exit()

tok = ''
try:
  config = SafeConfigParser()
  config.read('/home/pi/Watchman/WatchmanConfig.ini')
  tok = config.get('ConfigVariables', 'token')
except:
  print 'Error reading telegram bot config'
  exitScript()

path = ['/home/pi/ftp/files/Pics','/home/pi/ftp/files/Vids','/home/pi/Pictures/PiCam','/home/pi/Pictures/USB1Cam','/home/pi/Videos/PiCam','/home/pi/Videos/USB1Cam']

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
    for p in path:
      for f in os.listdir(p):
          f = os.path.join(p, f)
          if os.path.isfile(f):
            ext = os.path.splitext(f)[-1].lower()
            #print ext
            if ext == ".jpg" or ext == ".png":
              print 'uploading image file : '+f
              output = subprocess.check_output(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendPic.py',f])
              #if 'sent' in output:
              #  os.remove(f)
            if ext == ".mp4" or ext == ".mkv":
              print 'uploading video file : '+f
              output = subprocess.check_output(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendVid.py',f])
              #if 'sent' in output:
              #  os.remove(f)

    print 'Finished uploading files..'
    exitScript()
  except Exception as e:
    exitScript(e)
else:
  print 'No internet, upload script terminated !'
  exitScript()
