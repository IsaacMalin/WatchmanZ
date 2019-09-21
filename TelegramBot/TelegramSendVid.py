#!/usr/bin/env python
import telepot
import sys
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

vidPath = str(sys.argv[1])

bot = telepot.Bot(token)
try:
  bot.sendVideo (chat_id, video=open(vidPath))
  print 'sent'
except Exception as e:
  print e
  print 'failed'

