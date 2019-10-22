#!/usr/bin/env python
import subprocess
import RPi.GPIO as GPIO
import serial
import sys
import stat
import os
import time

def dev_exists(path):
  try:
    os.stat(path)
  except Exception as e:
    #print('Error: {}'.format(e))
    return False
  return True

for x in range(5):
  usbdev = '/dev/ttyUSB'+str(x)
  #print(dev_exists(usbdev))
  if dev_exists(usbdev):
    #print('Usb device found!!')
    #print(usbdev)
    break
  else:
    if x > 3:
      msg = 'Please connect ftdi usb programmer or try another usb port.'
      print(msg)
      FNULL = open(os.devnull, 'w')
      subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','Connect Programmer!!','2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
      c = open("/home/pi/Watchman/usbSerialBusy.txt","w")
      status = c.write('0')
      c.close()
      sys.exit()
  time.sleep(0.5)

status = '1'
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
if status == '1':
  print('USB device is busy, try again later..')
  sys.exit()

c = open("/home/pi/Watchman/usbSerialBusy.txt","w")
status = c.write('1')
c.close()

ssid = ''
pswd = ''
name = ''
ip = ''
hubip = ''
routerip = ''

msg = 'Connect and reset sensor'
FNULL = open(os.devnull, 'w')
subprocess.call(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
FNULL = open(os.devnull, 'w')
subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',' ','3'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)

baud = 9600
serial = serial.Serial(
  port=usbdev,
  baudrate=baud,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)

for x in range(20):
  #print(str(x)+'. '+str(baud))
  buf = serial.readline()
  if 'waiting' in buf.lower():
    break
  else:
    serial.baudrate = baud
    if baud == 9600:
      baud = 115200
    else:
      baud = 9600

loopcount = 0
while loopcount < 20:
  loopcount += 1
  #print(str(loopcount)+'. Connect, reset sensor') #1
  buf = serial.readline()
  #print(buf) #2
  if len(buf)>1:
    loopcount = 0
  if 'waiting for command' in buf.lower():
    msg = 'Sensor found!!'
    FNULL = open(os.devnull, 'w')
    subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
    time.sleep(0.5)
    wait = True
    count = 0
    while wait and count < 10:
      serial.write('R\n')
      buf = serial.readline()
      if buf:
        count = 0
      if '~' in buf:
        #print(buf) #3
        var = buf.split('~')
        try:
          ssid = var[0]
          pswd = var[1]
          name = var[2]
          ip = var[3]
          hubip = var[4]
          routerip = var[5]
        except:
          print('Error reading sensor configuration, please retry later or configure again.')
          c = open("/home/pi/Watchman/usbSerialBusy.txt","w")
          status = c.write('0')
          c.close()
          sys.exit()
        print('['+str(name)+']\nSSID:'+str(ssid)+'\nPSWD:'+str(pswd)+'\nIP:'+str(ip)+'\nG-Hub IP:'+str(hubip))+'\nRouter:'+str(routerip)
        wait = False
        msg = 'Read Success!!'
        FNULL = open(os.devnull, 'w')
        subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
      count += 1
      time.sleep(0.1)
    if count >= 9:
      msg = 'No sensor response!!'
      FNULL = open(os.devnull, 'w')
      subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
      print('Sensor did not respond, please try again..')
    break
  time.sleep(0.1)
  if loopcount > 19:
    msg = 'No sensor detected.'
    FNULL = open(os.devnull, 'w')
    subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
    print(msg+' After sending sms, please connect sensor to programmer and restart it.')

#msg = 'Done reading sensor!!'
#FNULL = open(os.devnull, 'w')
#subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'3'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
c = open("/home/pi/Watchman/usbSerialBusy.txt","w")
status = c.write('0')
c.close()

serial.close()
