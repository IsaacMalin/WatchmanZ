#!/usr/bin/env python
import telepot
import sys
import os
from ConfigParser import SafeConfigParser

#check if gprs is activated
try:
  c = open("/home/pi/Watchman/useGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  err = 'Error: {}'.format(e)
  print err
  if 'No such file' in err:
    c = open("/home/pi/Watchman/useGprs.txt","w")
    status = c.write('0')
    c.close()
  sys.exit()
if status == '1':
  print'gprs mode is active..'
  sys.exit()

config = SafeConfigParser()
try:
  config.read('/home/pi/Watchman/WatchmanConfig.ini')

  username = config.get('ConfigVariables', 'username')
  chat_id = config.get('ConfigVariables', 'chatid')
  token = config.get('ConfigVariables', 'token')
except:
  print 'failed'
  sys.exit()

vidPath = str(sys.argv[1])

bot = telepot.Bot(token)
try:
  bot.sendVideo (chat_id, video=open(vidPath))
  print 'sent'
  os.remove(vidPath)
except Exception as e:
  print e
  print 'failed'

