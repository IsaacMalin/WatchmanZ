#!/usr/bin/env python
import telepot
import sys
import subprocess
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
try:
  config.read('/home/pi/Watchman/WatchmanConfig.ini')

  username = config.get('ConfigVariables', 'username')
  chat_id = config.get('ConfigVariables', 'chatid')
  token = config.get('ConfigVariables', 'token')
except:
  print 'failed'
  sys.exit()


picPath = str(sys.argv[1])
#print picPath

#resize img if using gprs..
status = '0'
try:
  c = open("/home/pi/Watchman/useGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  pass

if status == '1':
  print 'GPRS connection detected, compressing image..'
  subprocess.call(['sudo','convert',picPath,'-resize','160','pic-sm.jpg'])
  picPath = 'pic-sm.jpg'

bot = telepot.Bot(token)
try:
  print 'Sending image..'
  bot.sendPhoto (chat_id, photo=open(picPath))
  print 'sent'
except Exception as e:
  print 'failed'
subprocess.call(['sudo','rm','pic-sm.jpg'])
