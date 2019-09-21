#!/usr/bin/env python
import sys
from ConfigParser import SafeConfigParser

varName = sys.argv[1]
var = sys.argv[2]

print 'Saving variable: '+varName
config = SafeConfigParser()
config.read('/home/pi/Watchman/WatchmanConfig.ini')
if not config.has_section('ConfigVariables'):
  config.add_section('ConfigVariables')
config.set('ConfigVariables', str(varName), str(var))

with open('/home/pi/Watchman/WatchmanConfig.ini', 'w+') as configfile:
    config.write(configfile)
    configfile.close()
