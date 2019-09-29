#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import subprocess
from datetime import datetime

resetPin = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(resetPin, GPIO.OUT)

GPIO.output(resetPin, GPIO.LOW)
time.sleep(1/100)
GPIO.output(resetPin, GPIO.HIGH)

ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'
print "Sim800l has been reset!"

GPIO.cleanup()

time.sleep(10)

status = '0'
try:
  c = open("/home/pi/Watchman/useGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  pass
