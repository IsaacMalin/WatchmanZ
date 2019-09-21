#!/usr/bin/python
import sys
import subprocess
import time

adminNum = '0723942375'
print 'Calling Admin..'

subprocess.Popen(['sudo','/home/pi/Watchman/sim800l/checkSim800lEvents.py','>','/home/pi/Watchman/logs/checkSim800lEvents.log','2>&1'])
time.sleep(3)
subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub.py','callNumber',str(adminNum)])
