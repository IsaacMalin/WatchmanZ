#!/usr/bin/python
import sys
import subprocess
import time
import telepot
from ConfigParser import SafeConfigParser

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

error = 0
token = ''
msg = ''
REMOTE_SERVER = '8.8.8.8'

#subprocess.Popen(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
print 'Stopping checkSim800lEvents script..'
subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub.py','closeCheckSimEvents','1'])
time.sleep(2)
c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w")
status = c.write('1')
c.close()

print 'Starting gprs connection'
try:
  subprocess.call(['sudo','route','del','default','wlan0'])
  time.sleep(2)
  subprocess.call(['sudo','pon','rnet'])
  time.sleep(10)
  error = 0
except Exception as e:
  print 'Error: {}'.format(e)
  error = 1
  msg = 'Failed to activate GPRS, try again later..'

if error == 0:
  try:
    config = SafeConfigParser()
    config.read('/home/pi/Watchman/WatchmanConfig.ini')
    token = config.get('ConfigVariables', 'token')
    username = config.get('ConfigVariables', 'username')
    error = 0
  except:
    msg = 'Please configure telegram bot first.'
    error = 1

if error == 0:
  if checkInternet(REMOTE_SERVER):
    error = 0
  else:
    msg = 'No internet connection, check airtime balance and try again.'
    error = 1

if error == 0:
  try:
    bot = telepot.Bot(token)
    data = bot.getMe()
    error = 0
  except:
    msg = 'Failed to start telegram bot, check token and try again.'
    error = 1

if error == 0:
  c = open("/home/pi/Watchman/useGprs.txt","w")
  status = c.write('1')
  c.close()
  msg = 'GPRS connected, you will not receive SMS or Calls. Pictures and msgs will be sent to you via telegram. GPRS will deactivate if internet is unavailable.'
  result =  subprocess.check_output(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(msg),'0'])
  print result
  if 'failed' in result:
    error = 1
    msg = 'Failed to send a message to you via Telegram, check airtime balance and try again.'


c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w")
status = c.write('0')
c.close()

if error == 0:
  print 'GPRS connected!!'
  pass
else:
  print 'Closing gprs connection'
  subprocess.call(['sudo','poff','rnet'])
  #subprocess.call(['sudo','route','del','default'])
  subprocess.check_output(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
  c = open("/home/pi/Watchman/useGprs.txt","w")
  status = c.write('0')
  c.close()
  print msg
  subprocess.call(['sudo','/home/pi/Watchman/sendSMS.py',str(msg)])
