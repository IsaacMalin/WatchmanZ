#!/usr/bin/env python
import os
import time
import sys
from datetime import datetime

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'

path = ['/home/pi/Pictures/IpCam','/home/pi/Pictures/PiCam','/home/pi/Pictures/USB1Cam','/home/pi/Videos/IpCam','/home/pi/Videos/PiCam','/home/pi/Videos/USB1Cam']

now = time.time()

print 'Removing files caputured before '+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now - 7 * 86400))

for p in path:
  for f in os.listdir(p):
    f = os.path.join(p, f)
    if (os.stat(f).st_mtime) < (now - 7 * 86400):
      print 'deleting file { '+f+' } captured on '+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(f).st_mtime))

      if os.path.isfile(f):
        os.remove(f)

print 'Deleting files larger than 5M in logs..'

os.system('sudo find /home/pi/Watchman/logs/*.log -type f -size +5M -delete')
