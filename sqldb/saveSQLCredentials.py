#!/usr/bin/env python
import sys
from ConfigParser import SafeConfigParser

usr = sys.argv[1]
pswd = sys.argv[2]
db = sys.argv[3]

config = SafeConfigParser()
config.read('sqlCredentials.ini')
if not config.has_section('credentials'):
  config.add_section('credentials')
config.set('credentials', 'username', usr)
config.set('credentials', 'password', pswd)
config.set('credentials', 'database', db)

with open('sqlCredentials.ini', 'w') as configfile:
    config.write(configfile)
