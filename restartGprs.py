#!/usr/bin/python
import time
import subprocess
import sys

try:
  c = open("/home/pi/Watchman/useGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  sys.exit()

if status == '1':
  time.sleep(10)
  subprocess.call(['sudo','/home/pi/Watchman/activateGprs.py'])
