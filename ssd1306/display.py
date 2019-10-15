#!/usr/bin/python3
import subprocess
import sys
import time

try:
  status = '1'
  count = 0
  while status == '1' and count<10:
    print(str(count)+'. Waiting to print to screen..')
    c = open("/home/pi/Watchman/ssd1306/display.txt","r")
    status = c.read()
    status = status.strip()
    c.close()
    count += 1
    time.sleep(1)
except Exception as e:
  err = 'Error: {}'.format(e)
  print(err)
  if 'No such file' in err:
    c = open("/home/pi/Watchman/ssd1306/display.txt","w+")
    status = c.write('0')
    c.close()
  sys.exit()

c = open("/home/pi/Watchman/ssd1306/display.txt","w+")
status = c.write('1')
c.close()

#get arguments
msg = sys.argv[1]
section = sys.argv[2]

push_msg = str(section)+'~'+str(msg)
subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub3.py','pushToDisplay',push_msg])

c = open("/home/pi/Watchman/ssd1306/display.txt","w+")
status = c.write('0')
c.close()
time.sleep(0.1)
