#!/usr/bin/python
import sys
import subprocess
import time

msg = sys.argv[1]
sendSms = sys.argv[2]

print 'Stopping checkSim800lEvents script..'
subprocess.call(['sudo','/home/pi/Watchman/mqtt/mqttPub.py','closeCheckSimEvents','1'])
time.sleep(2)
c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w")
status = c.write('1')
c.close()

print 'Starting gprs connection'
subprocess.call(['sudo','pon','rnet'])
time.sleep(2)
subprocess.call(['sudo','route','del','default'])
try:
  subprocess.call(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(msg),str(sendSms)])
  print 'msg sent via gprs'
except:
  print 'Sending via gprs failed, sending via sms..'
  c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w")
  status = c.write('0')
  c.close()
  subprocess.call(['sudo','/home/pi/Watchman/sendSMS.py',str(msg)])
  sys.exit()

print 'Closing gprs connection'
subprocess.call(['sudo','poff','rnet'])
time.sleep(2)
c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w")
status = c.write('0')
c.close()
subprocess.call(['sudo','/home/pi/Watchman/sim800l/checkSim800lEvents.py'])
