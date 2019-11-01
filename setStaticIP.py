#!/usr/bin/env python
import sys
import subprocess

try:
  ip = sys.argv[1]
  router = sys.argv[2]
  dns = sys.argv[3]

  o = subprocess.call(['sudo','cp','/etc/dhcpcd.default','/etc/dhcpcd.temp'])
  p = open("/etc/dhcpcd.temp","a+")
  p.write('\ninterface wlan0\nstatic ip_address='+ip+'\nstatic routers='+router+'\nstatic domain_name_servers='+dns)
  p.close()

  o = subprocess.call(['sudo','cp','/etc/dhcpcd.temp','/etc/dhcpcd.conf'])
  o = subprocess.call(['sudo','rm','/etc/dhcpcd.temp'])
  error = 0
except:
  error = 1

if error == 0:
  subprocess.call(['sudo','/home/pi/Watchman/saveWatchmanConfig.py','staticip',str(ip)])
  print 'done'
else:
  print 'error'

