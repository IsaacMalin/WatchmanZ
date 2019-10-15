#!/usr/bin/env python
import subprocess

#ssid = ''
#try:
#  ssid = subprocess.check_output(['/home/pi/Watchman/wifiSSID.py'])
#except Exception as e:
#  print 'Error: {}'.format(e)
#  pass
#if ssid:
#  subprocess.call(['sudo','/home/pi/Watchman/ssd1306/display.py',str(ssid),'4'])

#check the battery status and if we are running on mains power or battery power
status = ''
level = ''
try:
  b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","r")
  msg = b.read()
  b.close()
  if len(msg) > 4:
    splitMsg = msg.split('#')
    source = splitMsg[0]
    level = splitMsg[1]
    if(source == '1'):
      status = 'MAINS ON'
    else:
      status = 'MAINS OFF'
except:
  b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","w+")
  b.write(' ')
  b.close()

if level:
  subprocess.call(['sudo','/home/pi/Watchman/ssd1306/display.py',str(level)+' '+str(status),'5'])
