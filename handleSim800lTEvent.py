#!/usr/bin/env python
import sys
import RPi.GPIO as GPIO
import subprocess

greenLed = 13
GPIO.setmode(GPIO.BOARD)
GPIO.setup(greenLed, GPIO.OUT, initial = 0)

event = sys.argv[1]
msg = sys.argv[2]

if event == 'S': #if we get any sms msg through Sim800lT which isnt from admin, fwd to telegram
  print 'fowarding sms message to Telegram..'
  msg = "SMS from GSM Module: ["+msg+"]"
  output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", msg, '1'])

else:
  print 'fowarding gsm module message to Telegram..'
  msg = "Message from GSM Module: ["+msg+"]"
  output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", msg, '1'])

GPIO.output(greenLed,GPIO.LOW)
GPIO.cleanup()
