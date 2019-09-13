#!/usr/bin/env python
import sys
from ConfigParser import SafeConfigParser

username = sys.argv[1]
chatId = sys.argv[2]
token = sys.argv[3]

config = SafeConfigParser()
config.read('TelegramBotConfig.ini')
if not config.has_section('credentials'):
  config.add_section('credentials')
config.set('credentials', 'username', username)
config.set('credentials', 'chatid', chatId)
config.set('credentials', 'token', token)

with open('TelegramBotConfig.ini', 'w') as configfile:
    config.write(configfile)
