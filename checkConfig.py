#!/usr/bin/env python
import subprocess
import socket
import telepot
from ConfigParser import SafeConfigParser

connectivity = ''
ssid = ''
ip = ''
net = ''
username = ''
token = ''
botStatus = ''
adminNo = ''
callbackNo = ''
gpsStatus = ''

try:
  config = SafeConfigParser()
  config.read('/home/pi/Watchman/WatchmanConfig.ini')
except:
  username = 'Not_set'
  token = 'Not_set'
  adminNo = 'Not_set'
  callbackNo = 'Not_set'
try:
  username = config.get('ConfigVariables', 'username')
except:
  username = 'Not_set'
try:
  tok = config.get('ConfigVariables', 'token')
  if len(str(tok)) > 30:
    token = 'Token set'
  else:
    token = 'Invalid'
except:
  token = 'Not_set'
try:
  adminNo = config.get('ConfigVariables', 'admin_no')
except:
  adminNo = 'Not_set'
try:
  callbackNo = config.get('ConfigVariables', 'callback_no')
except:
  callbackNo = 'Not_set'
try:
  c = open("/home/pi/Watchman/useGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
  if status == '1':
    gprsStatus = 'Active'
  elif status == '0':
    gprsStatus = 'Disabled'
  else:
    gprsStatus = 'Unknown'
except:
  gprsStatus  = 'Not_set'

def checkInternet(hostname):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80))
    s.close()
    return True
  except Exception as e:
     pass
  return False

REMOTE_SERVER = 'www.google.com'
try:
    ps = subprocess.Popen(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
    connectivity = 'Connected'
    ssid = output.split('"')[1]
    ip = subprocess.check_output(['sudo','hostname','-I']).strip()
except:
    # grep did not match any lines
    connectivity = 'Not connected'
    ip = 'None'

if checkInternet(REMOTE_SERVER):
  net = 'Connected'
else:
  net = 'Unavailable'

if  'C' in net:
  try:
    bot = telepot.Bot(tok)
    data = bot.getMe()
    botStatus = 'Connected'
  except:
    botStatus = 'Offline'
else:
  botStatus = 'Unknown'

print '[WiFi]\nStatus: '+connectivity+'\nSSID: '+ssid+'\nIP: '+ip+'\nInternet: '+net+'\n|[Telegram]\nUsername: '+username+'\nToken: '+token+'\nBot: '+botStatus+'\n|[GSM]\nAdmin: '+adminNo+'\nCallback: '+callbackNo+'\nGPRS: '+gprsStatus
