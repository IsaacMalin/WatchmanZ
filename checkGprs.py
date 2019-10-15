#!/usr/bin/python
import subprocess
import sys
import telepot
import time
from ConfigParser import SafeConfigParser
from datetime import datetime

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'

#check if this script is already running
status = '1'
try:
  c = open("/home/pi/Watchman/checkingGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  err = 'Error: {}'.format(e)
  print err
  if 'No such file' in err:
    c = open("/home/pi/Watchman/checkingGprs.txt","w+")
    status = c.write('0')
    c.close()
  sys.exit()
if status == '1':
  print'checking GPRS ongoing..'
  sys.exit()
else:
  c = open("/home/pi/Watchman/checkingGprs.txt","w")
  status = c.write('1')
  c.close()

def exitScript(e):
  print 'Exit status: {}'.format(e)
  c = open("/home/pi/Watchman/checkingGprs.txt","w")
  status = c.write('0')
  c.close()
  sys.exit()

try:
  #check if gprs mode is active
  try:
    c = open("/home/pi/Watchman/useGprs.txt","r")
    status = c.read()
    status = status.strip()
    c.close()
  except Exception as e:
    err = 'Error: {}'.format(e)
    print err
    if 'No such file' in err:
      c = open("/home/pi/Watchman/useGprs.txt","w+")
      status = c.write('0')
      c.close()
    exitScript('No useGprs.txt file..')
  if not status == '1':
    exitScript('GPRS mode is inactive')

  config = SafeConfigParser()
  token = ''
  try:
    config.read('/home/pi/Watchman/WatchmanConfig.ini')
    token = config.get('ConfigVariables', 'token')
  except:
    pass

  c = open("/home/pi/Watchman/activatingGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
  if status == '1':
    exitScript('GPRS is still being activated..')

  try:
    c = open("/home/pi/Watchman/closingGprs.txt","r")
    status = c.read()
    status = status.strip()
    c.close()
    if status == '1':
      exitScript('GPRS is being closed..')
  except:
    c = open("/home/pi/Watchman/closingGprs.txt","w+")
    status = c.write('0')
    c.close()

  def checkInternet(hostname):
    print 'Checking Internet Connectivity..'
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
       print 'Internet Unavailable, Error: {}'.format(e)
       return False
  REMOTE_SERVER = '8.8.8.8'

  if not checkInternet(REMOTE_SERVER):
    print 'No internet, restarting ppp connection'
    subprocess.call(['sudo','route','del','default','wlan0'])
    time.sleep(2)
    count = 0
    while checkInternet(REMOTE_SERVER)==False and count < 5:
      print str(count)+'. Internet unavailable, trying to activate GPRS..'
      count += 1
      subprocess.call(['sudo','poff','rnet'])
      if count > 2:
        time.sleep(5)
        subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
        time.sleep(5)
      time.sleep(5)
      subprocess.call(['sudo','pon','rnet'])
      time.sleep(10)
    if count > 5:
      print 'Unable to get internet via GPRS!!'
    else:
      print 'Internet connected!!'

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
    subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GPRS Disconnected','1'])
    subprocess.call(['sudo','poff','rnet'])
    #subprocess.call(['sudo','route','del','default'])
    subprocess.check_output(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
    c = open("/home/pi/Watchman/useGprs.txt","w")
    status = c.write('0')
    c.close()
    #subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
    msg = 'There is no connection to Telegram, GPRS has been deactivated, check airtime balance and reconnect GPRS. Send SMS \'Use_gprs\''
    subprocess.Popen(['sudo','/home/pi/Watchman/sendSMS.py',str(msg)])
  else:
    print 'Bot available, leaving GPRS active..'

except Exception as e:
  exitScript(e)

exitScript('Done checking GPRS!!')
