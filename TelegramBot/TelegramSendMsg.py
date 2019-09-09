#!/usr/bin/env python
import telepot
import sys
import subprocess
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('/home/pi/Watchman/TelegramBot/TelegramBotConfig.ini')

username = config.get('credentials', 'username')
chat_id = config.get('credentials', 'chatid')
token = config.get('credentials', 'token')

msg = str(sys.argv[1])
sendSms = sys.argv[2]
#print msg

bot = telepot.Bot(token)
try:
  bot.sendMessage(chat_id, str(msg))
  print 'sent'
except Exception as e:
  print 'failed to send via Telegram'
  if sendSms == '1':
    print 'Trying to send via SMS..'
    c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","w+")
    c.write(msg)
    c.close()

    p = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","a+")
    p.write(msg+', ')
    p.close()


    output = subprocess.Popen(["sudo", "/home/pi/Watchman/sendSMS.py", msg+"\n(Sending via Telegram Failed!)"])

