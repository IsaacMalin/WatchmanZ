#!/usr/bin/python
import subprocess
import sys

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
  print'gprs mode is inactive..'
  sys.exit()

print 'Closing gprs connection'
subprocess.call(['sudo','poff','rnet'])
#subprocess.call(['sudo','route','del','default'])
subprocess.check_output(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
c = open("/home/pi/Watchman/useGprs.txt","w")
status = c.write('0')
c.close()

msg = 'GPRS has been deactivated, to reconnect, Send SMS \'Use_gprs\''
subprocess.call(['sudo','/home/pi/Watchman/sendSMS.py',str(msg)])
