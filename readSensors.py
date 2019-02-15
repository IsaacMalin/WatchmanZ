#!/usr/bin/env python
import subprocess
import RPi.GPIO as GPIO
import time
from datetime import datetime

ledVib = 15
ledMotion = 16
vib = 18
motion = 11
ldr = 13
switchIR = 12
pwr = 22

#method to be invoked once vibrations have been detected
def vibDetected(channel):
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print '['+ts+'] Vibration detected!!'
  global led
  GPIO.output(ledVib,GPIO.HIGH)
  f = open("/home/pi/Watchman/allowToSendVibMsg.txt","r")
  authorizeVibMsg = f.read()
  f.close()
  authorizeVibMsg = authorizeVibMsg.strip()
  if authorizeVibMsg == '1':
    ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    ms = datetime.now().strftime("%H:%M:%S")
    VibSensorMsg = 'Vibration detected at '+ms
    #send message to telegram user
    output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", VibSensorMsg])
    o = open("/home/pi/Watchman/imageOrVideoCam2.txt","r")
    option = o.read()
    o.close()
    option = option.strip()
    #if GPIO.input(ldr):
    #  GPIO.output(switchIR, GPIO.HIGH)
    if option == 'i':
      imgPath = '/home/pi/Pictures/USB1Cam/'
      imgName = 'USB1Cam['+ts+'].jpg'
      path = imgPath+imgName
      #take image from usb1-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takeUSB1CamImg.sh", path])
      #send image to telegram user
      output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendPic.py", path])
    if option == 'v':
      vidPath = '/home/pi/Videos/USB1Cam/'
      vidName = 'USB1Cam['+ts+'].avi'
      path = vidPath+vidName
      #take video from usb1-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takeUSB1CamVid.sh", path, "5"])
      #send video to telegram user
      output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendVid.py", path])
    #GPIO.output(switchIR, GPIO.LOW)

  GPIO.output(ledVib,GPIO.LOW)

#method to be invoked once motion has been detected
def motionDetected(channel):
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print '['+ts+'] Motion detected!!'
  global led
  GPIO.output(ledMotion,GPIO.HIGH)
  f = open("/home/pi/Watchman/allowToSendMotionMsg.txt","r")
  authorizeMotionMsg = f.read()
  f.close()
  authorizeMotionMsg = authorizeMotionMsg.strip()
  if authorizeMotionMsg == '1':
    ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    ms = datetime.now().strftime("%H:%M:%S")
    MotionSensorMsg = 'Motion detected at '+ms
    #send message to telegram user
    output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", MotionSensorMsg])
    o = open("/home/pi/Watchman/imageOrVideoCam1.txt","r")
    option = o.read()
    o.close()
    option = option.strip()
    if GPIO.input(ldr):
      GPIO.output(switchIR, GPIO.HIGH)
    if option == 'i':
      piImgPath = '/home/pi/Pictures/PiCam/'
      piImgName = 'Pi-Cam['+ts+'].jpg'
      path = piImgPath+piImgName
      #take image from pi-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takePiCamImg.sh", path])
      #send image to telegram user
      output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendPic.py", path])
    if option == 'v':
      piVidPath = '/home/pi/Videos/PiCam/'
      piVidName = 'Pi-Cam['+ts+'].mp4'
      path = piVidPath+piVidName
      #take video from pi-camera
      output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takePiCamVid.sh", path, "5000"])
      #send video to telegram user
      output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendVid.py", path])
    GPIO.output(switchIR, GPIO.LOW)

  GPIO.output(ledMotion,GPIO.LOW)

#method to invoke when low power is detected
def lowBattery(channel):
  if GPIO.input(pwr):
    print 'Low Battery!!'
    ms = datetime.now().strftime("%H:%M:%S")
    lowBatteryMsg = "["+ms+"] System reports battery is getting low!!"
    output = subprocess.Popen(["sudo", "/home/pi/Watchman/TelegramBot/TelegramSendMsg.py", lowBatteryMsg])

#check if script is already running
c = open("/home/pi/Watchman/isSensRunning.txt","r")
status = c.read()
status = status.strip()
c.close()
if status == '1':
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] readSensor already running!!'
  exit()
#setup the GPIO Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledVib, GPIO.OUT, initial = 0)
GPIO.setup(ledMotion, GPIO.OUT, initial = 0)
GPIO.setup(vib, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(motion, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(ldr, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(switchIR, GPIO.OUT, initial = 0)
GPIO.setup(pwr, GPIO.IN, GPIO.PUD_DOWN)

#add event detection to pins
GPIO.add_event_detect(vib, GPIO.RISING, vibDetected, 7000)
GPIO.add_event_detect(motion, GPIO.RISING, motionDetected, 7000)
GPIO.add_event_detect(pwr, GPIO.RISING, lowBattery, 10000)
ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+'] Sensor monitoring running..'
c = open("/home/pi/Watchman/isSensRunning.txt","w+")
status = c.write('1')
c.close()
try:
  while(True):
    time.sleep(1)

except:
  GPIO.cleanup()
  c = open("/home/pi/Watchman/isSensRunning.txt","w+")
  status = c.write('0')
  c.close()
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] Exiting..'

