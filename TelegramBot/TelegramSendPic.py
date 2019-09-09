#!/usr/bin/env python
import telepot
import sys
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('/home/pi/Watchman/TelegramBot/TelegramBotConfig.ini')

username = config.get('credentials', 'username')
chat_id = config.get('credentials', 'chatid')
token = config.get('credentials', 'token')


picPath = str(sys.argv[1])
#print picPath

bot = telepot.Bot(token)
try:
  bot.sendPhoto (chat_id, photo=open(picPath))
  print 'sent'
except Exception as e:
  print 'failed'
