#!/usr/bin/python
import sys
import subprocess
import time

sms = sys.argv[1]
print 'sending sms...'

#subprocess.Popen(['sudo','/home/pi/Watchman/sim800l/checkSim800lEvents.py','>','/home/pi/Watchman/logs/checkSim800lEvents.log','2>&1'])
subprocess.Popen(['sudo','/home/pi/Watchman/sim800l/checkSim800lEvents.py'])
time.sleep(3)
subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub.py','sendSMS',str(sms)])


