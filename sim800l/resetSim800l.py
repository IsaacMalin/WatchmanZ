#!/usr/bin/python

import RPi.GPIO as GPIO
import time

resetPin = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(resetPin, GPIO.OUT)

GPIO.output(resetPin, GPIO.LOW)
time.sleep(1/100)
GPIO.output(resetPin, GPIO.HIGH)

print "Sim800l has been reset!"

GPIO.cleanup()
