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

try:
  name = sys.argv[1]
  ssid = sys.argv[2]
  pswd = sys.argv[3]
  ip = sys.argv[4]
  hubip = sys.argv[5]
  routerip = sys.argv[6]
except:
  print('Error configuring sensor, please retry..')
  sys.exit()

c = open("/home/pi/Watchman/usbSerialBusy.txt","w")
status = c.write('1')
c.close()

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
  #print(str(x)+'. '+str(baud)) #1
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
  #print(str(loopcount)+'. Connect, reset sensor') #2
  buf = serial.readline()
  #print(buf) #3
  if len(buf)>1:
    loopcount = 0
  if 'waiting for command' in buf.lower():
    msg = 'Sensor found!!'
    FNULL = open(os.devnull, 'w')
    subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
    serial.write('C\n')
    time.sleep(0.5)
    wait = True
    count = 0
    while wait and count < 10:
      buf = serial.readline()
      if buf:
        count = 0
      if 'waiting for data' in buf.lower():
        serial.write(str(name)+'~'+str(ssid)+'~'+str(pswd)+'~'+str(ip)+'~'+str(hubip)+'~'+str(routerip)+'~\n')
        time.sleep(1)
        wait = False
        buf = serial.readline()
        #print(buf) #4
        if '^' in buf:
          msg = 'Sensor Configured!!'
          FNULL = open(os.devnull, 'w')
          subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
          print(msg)
        else:
          msg = 'Configuration failed'
          FNULL = open(os.devnull, 'w')
          subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',msg,'2'], stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)
          print(msg+'. Please try again.')
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
