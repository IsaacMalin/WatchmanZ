#!/usr/bin/python
import subprocess
import sys

msg = sys.argv[1]

try:
  b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","w")
  b.write(msg)
  b.close()
  subprocess.call(['sudo','/home/pi/Watchman/ssd1306/updateDisplay.py'])
except Exception as e:
  print 'Error: {}'.format(e)
