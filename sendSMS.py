#!/usr/bin/python
import sys
import subprocess
import time

adminNum = '0723942375'
sms = sys.argv[1]
print 'sending sms...'

subprocess.Popen(['sudo','/home/pi/Watchman/sim800l/checkSim800lEvents.py'])
time.sleep(5)
subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub.py','sendSMS',adminNum+'^'+str(sms)])


