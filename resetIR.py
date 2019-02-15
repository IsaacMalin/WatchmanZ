#!/usr/bin/env python
import RPi.GPIO as GPIO

switchIR = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(switchIR, GPIO.OUT, initial = 0)

GPIO.output(switchIR, GPIO.LOW)
