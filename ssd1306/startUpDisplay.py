#!/usr/bin/python3
from configparser import SafeConfigParser

config = SafeConfigParser()

config.read('/home/pi/Watchman/ssd1306/displayData.ini')
if not config.has_section('messages'):
  config.add_section('messages')
config.set('messages', '1', 'Booting')
config.set('messages', '2', 'No Sensor Message')
config.set('messages', '3', ' ')
config.set('messages', '4', 'Not Connected')
config.set('messages', '5', 'Unknown')

with open('/home/pi/Watchman/ssd1306/displayData.ini', 'w+') as configfile:
    config.write(configfile)
    configfile.close()
