#!/usr/bin/env python
import time
from datetime import datetime

c = open("/home/pi/Watchman/TelegramBot/isBotRunning.txt","w+")
status = c.write('0')
c.close()

s = open("/home/pi/Watchman/isSensRunning.txt","w+")
status = s.write('0')
s.close()

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print 'Initialized sensor and bot variables on '+ts
