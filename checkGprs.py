#!/usr/bin/python
import subprocess
import sys
import telepot
import time
from ConfigParser import SafeConfigParser
from datetime import datetime

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'

config = SafeConfigParser()
token = ''
try:
  config.read('/home/pi/Watchman/WatchmanConfig.ini')
  token = config.get('ConfigVariables', 'token')
except:
  pass

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
  print 'No internet, restarting ppp connection'
  subprocess.call(['sudo','pon','rnet'])
  time.sleep(10)

def checkBot():
  try:
      bot = telepot.Bot(token)
      data = bot.getMe()
      return True
  except Exception as e:
      #print 'Error: {}'.format(e)
      return False


if not checkBot():
  print 'Bot unavailable, closing GPRS..'
  subprocess.call(['sudo','poff','rnet'])
  #subprocess.call(['sudo','route','del','default'])
  subprocess.check_output(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
  c = open("/home/pi/Watchman/useGprs.txt","w")
  status = c.write('0')
  c.close()
  subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
  msg = 'There is no connection to Telegram, GPRS has been deactivated, check airtime balance and reconnect GPRS. Send SMS \'Use_gprs\''
  subprocess.Popen(['sudo','/home/pi/Watchman/sendSMS.py',str(msg)])
else:
  print 'Bot available, leaving GPRS active..'
