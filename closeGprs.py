#!/usr/bin/python
import subprocess
import sys
import time

c = open("/home/pi/Watchman/closingGprs.txt","w+")
status = c.write('1')
c.close()
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
if not status == '1':
  print'gprs mode is already disabled..'
  #sys.exit()

c = open("/home/pi/Watchman/activatingGprs.txt","r")
status = c.read()
status = status.strip()
c.close()
if status == '1':
  print 'GPRS is still being activated try later..'
  sys.exit()

print 'Closing gprs connection'
subprocess.call(['sudo','poff','rnet'])
#subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
#subprocess.call(['sudo','route','del','default'])
subprocess.check_output(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
msg = 'GPRS has been deactivated, to reconnect, Send SMS \'Use_gprs\''
time.sleep(2)
c = open("/home/pi/Watchman/useGprs.txt","w")
status = c.write('0')
c.close()
c = open("/home/pi/Watchman/closingGprs.txt","w+")
status = c.write('0')
c.close()
subprocess.call(['sudo','/home/pi/Watchman/sendSMS.py',str(msg)])
#time.sleep(10)
#subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub.py','closeCheckSimEvents','1'])
