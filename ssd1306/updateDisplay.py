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

try:
  c = open("/home/pi/Watchman/usbSerialBusy.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  err = 'Error: {}'.format(e)
  #print err
  if 'No such file' in err:
    print('Error, please try again..')
    c = open("/home/pi/Watchman/usbSerialBusy.txt","w+")
    status = c.write('0')
    c.close()
  sys.exit()
if status != '1':
  subprocess.call(['sudo','/home/pi/Watchman/ssd1306/display.py','No New Sensor Message','2'])
  subprocess.call(['sudo','/home/pi/Watchman/ssd1306/display.py',' ','3'])
