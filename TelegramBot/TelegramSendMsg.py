#!/usr/bin/env python
import telepot
import sys

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
#print msg

bot = telepot.Bot(token)
try:
  bot.sendMessage(chat_id, str(msg))
  print 'sent'
except Exception as e:
  print 'failed'
