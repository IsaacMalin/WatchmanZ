#!/usr/bin/python
import sys
import subprocess
import time

#check if gprs is activated
try:
  c = open("/home/pi/Watchman/useGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  err = 'Error: {}'.format(e)
  print err
  if 'No such file' in err:
    c = open("/home/pi/Watchman/useGprs.txt","w")
    status = c.write('0')
    c.close()
  sys.exit()
if status == '1':
  print'gprs mode is active..'
  sys.exit()

sms = sys.argv[1]
print 'sending sms...'

#subprocess.Popen(['sudo','/home/pi/Watchman/sim800l/checkSim800lEvents.py','>>','/home/pi/Watchman/logs/checkSim800lEvents.log','2>&1'])
subprocess.Popen(['sudo','/home/pi/Watchman/sim800l/checkSim800lEvents.py'])
time.sleep(3)
subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub.py','sendSMS',str(sms)])


