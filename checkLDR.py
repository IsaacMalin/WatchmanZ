#!/usr/bin/env python
import RPi.GPIO as GPIO

ldr = 13
switchIR = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ldr, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(switchIR, GPIO.OUT, initial = 0)

if GPIO.input(ldr):
  GPIO.output(switchIR, GPIO.HIGH)
