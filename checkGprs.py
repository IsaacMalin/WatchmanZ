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


def checkInternet(hostname):
  print 'pinging '+hostname
  try:
    result = subprocess.check_output(['sudo','ping','-c','2',hostname])
    #print result
    if 'bytes from '+hostname in result:
      print 'net available'
      return True
    else:
      print 'net not available'
      return False
  except Exception as e:
     print 'error, net not available'
     print 'Error: {}'.format(e)
     return False

REMOTE_SERVER = '8.8.8.8'

if not checkInternet(REMOTE_SERVER):
  print 'No Internet, closing GPRS..'
  subprocess.call(['sudo','poff','rnet'])
  #subprocess.call(['sudo','route','del','default'])
  subprocess.check_output(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
  c = open("/home/pi/Watchman/useGprs.txt","w")
  status = c.write('0')
  c.close()
  msg = 'There is no internet connection, GPRS has been deactivated, check airtime balance and reconnect GPRS. Send SMS \'Use_gprs\''
  subprocess.call(['sudo','/home/pi/Watchman/sendSMS.py',str(msg)])
else:
  print 'Internet available, leaving GPRS active..'
