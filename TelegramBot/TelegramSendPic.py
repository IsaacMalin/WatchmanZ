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

picPath = str(sys.argv[1])
#print picPath

print 'Sending pic to telegram..'
bot = telepot.Bot(token)
bot.sendPhoto (chat_id, photo=open(picPath))

print 'done sending pic!'
