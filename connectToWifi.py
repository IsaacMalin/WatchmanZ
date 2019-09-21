#!/usr/bin/env python
import sys
import subprocess
import time

ssid = sys.argv[1]
pswd = sys.argv[2]

try:
  essid = subprocess.check_output(['sudo','iwlist','wlan0','scan'])

  if ssid in essid:
    o = subprocess.call(['sudo','cp','/etc/wpa_supplicant/wpa_supplicant.default','/etc/wpa_supplicant/wpa_supplicant.temp'])
    p = open("/etc/wpa_supplicant/wpa_supplicant.temp","a+")
    p.write('\nnetwork={\n\tssid=\"'+ssid+'\"\n\tpsk=\"'+pswd+'\"\n}\n')
    p.close()

    o = subprocess.call(['sudo','cp','/etc/wpa_supplicant/wpa_supplicant.temp','/etc/wpa_supplicant/wpa_supplicant.conf'])
    o = subprocess.call(['sudo','rm','/etc/wpa_supplicant/wpa_supplicant.temp'])
    o = subprocess.call(['sudo','cp','/etc/dhcpcd.default','/etc/dhcpcd.conf'])

    subprocess.check_output(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])

    time.sleep(7)
    result = subprocess.check_output(['sudo','hostname','-I'])
    if len(str(result)) < 6:
      print 'ssid found but failed to connect, please confirm your password and try again.'
    else:
      print 'connected to SSID: '+ssid+' with IP: '+result+'\nPlease configure new static IP \n\'Set_static_IP|gatewayIP|routerIP|dns\''

  else:
    print 'ssid not found'
except:
  print 'Error occurred, please try again'

