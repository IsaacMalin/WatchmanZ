#!/usr/bin/env python
import time
from datetime import datetime
import subprocess

c = open("/home/pi/Watchman/TelegramBot/isBotRunning.txt","w+")
status = c.write('0')
c.close()

s = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w+")
status = s.write('0')
s.close()

m = open("/home/pi/Watchman/mqtt/mqttSub.txt","w+")
status = m.write('0')
m.close()

e = open("/home/pi/Watchman/checkingGprs.txt","w+")
status = e.write('0')
e.close()

c = open("/home/pi/Watchman/ssd1306/pushToDisplay.txt","w+")
status = c.write('0')
c.close()

c = open("/home/pi/Watchman/wifiDisconnected.txt","w+")
status = c.write('0')
c.close()

c = open("/home/pi/Watchman/wifiConnected.txt","w+")
status = c.write('0')
c.close()

c = open("/home/pi/Watchman/Images/takePiCamImg.txt","w+")
status = c.write('0')
c.close()

c = open("/home/pi/Watchman/Images/takeUSB1CamImg.txt","w+")
status = c.write('0')
c.close()

c = open("/home/pi/Watchman/Videos/takePiCamVid.txt","w+")
status = c.write('0')
c.close()

c = open("/home/pi/Watchman/Videos/takeUSB1CamVid.txt","w+")
status = c.write('0')
c.close()

subprocess.call(['/home/pi/Watchman/ssd1306/display.py','Booting..','1'])
subprocess.call(['/home/pi/Watchman/ssd1306/display.py','Searching..','4'])
ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print 'Initialized sensor and bot variables on '+ts
time.sleep(60)
subprocess.call(['sudo','wpa_cli','-i','wlan0','-a','/home/pi/Watchman/onWifiConnect.sh','-B'])
ssid = subprocess.check_output(['sudo','/home/pi/Watchman/wifiSSID.py'])
ip = subprocess.check_output(['hostname', '-I'])
ip = ip.replace('\n','').replace('\r','')
ip = ip.split('.')
shortip = ' [.'+ip[2]+'.'+ip[3]+']'
ssid = ssid.replace('\n','').replace('\r','')
if ssid:
  subprocess.call(['/home/pi/Watchman/ssd1306/display.py',str(ssid)+str(shortip),'4'])
