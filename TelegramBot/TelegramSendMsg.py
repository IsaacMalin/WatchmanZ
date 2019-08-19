#!/usr/bin/env python
import telepot
import sys
import subprocess

f = open("/home/pi/Watchman/TelegramBot/chatId.txt","r")
chat_id = f.read()
f.close()
#print chat_id

t = open("/home/pi/Watchman/TelegramBot/token.txt","r")
token = t.read()
t.close()
token = token.strip()
#print token

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
    output = subprocess.Popen(["sudo", "/home/pi/Watchman/sendSMS.py", msg+"\n(Sending via Telegram Failed!)"])

