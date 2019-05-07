#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import time, datetime
import telepot
from telepot.loop import MessageLoop
import random
import socket
import mysql.connector as mariadb
import MySQLdb


now = datetime.datetime.now()

def updateRegister(numOfValues,localID,value1,column1,value2=None,column2=None,value3=None,column3=None,value4=None,column4=None):
  mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
  cursor1 = mariadb_connection.cursor()
  try:
    cursor1.execute("SELECT * FROM registeredSensors WHERE localID = '%s'"%(str(localID)))
    result = cursor1.fetchall()
    rowCount = len(result)
    cursor1.close()
    #print rowCount
    if rowCount >= 1:
      for row in result:
        sensorName = row[1]
        vidLength = row[10]
        camType = row[7]
        camIP = row[8]
        cursor2 = mariadb_connection.cursor()
        try:
          if numOfValues == 1:
            cursor2.execute("UPDATE registeredSensors SET %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(localID)))
          elif numOfValues == 2:
            cursor2.execute("UPDATE registeredSensors SET %s = '%s', %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(localID)))
          elif numOfValues == 3:
            cursor2.execute("UPDATE registeredSensors SET %s = '%s', %s = '%s', %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(column3),str(value3),str(localID)))
          elif numOfValues == 4:
            cursor2.execute("UPDATE registeredSensors SET %s = '%s', %s = '%s', %s = '%s', %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(column3),str(value3),str(column4),str(value4),str(localID)))
          else:
            return '0','0','0','0','0'
          rowCount = cursor2.rowcount
          cursor2.close()
          mariadb_connection.commit()
          #print rowCount
          if rowCount >= 1:
            return '1',sensorName,vidLength,camType,camIP
          else:
            return 'A',sensorName,vidLength,camType,camIP
        except mariadb.Error as error:
          print("Error: {}".format(error))
          return '0','0','0','0','0'
    else:
      return '0','0','0','0','0'
  except mariadb.Error as error:
    print("Error: {}".format(error))
    return '0','0','0','0','0'
  mariadb_connection.close()

#use this function to check if ip address is valid
def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def action(msg):
    chat_id = msg['chat']['id']
    username = str(msg['chat']['first_name'])
    f = open("/home/pi/Watchman/TelegramBot/username.txt", "r")
    authorizedUser = f.read()
    authorizedUser = authorizedUser.strip()
    f.close()

    if username == authorizedUser:
        file = open("/home/pi/Watchman/TelegramBot/chatId.txt","w+")
        file.write(str(chat_id))
        file.close()
        command = msg['text']
        commandL = command.lower()
        commandS = command.split("_")

        ts = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        print '['+ts+'] Received: %s' % command

        GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey", "wasup", "sasa", "bonjour", "howdy", "how are you", "vipi")
        GREETING_RESPONSES = ["Hi", "Hey", "Hello", "Hi there..", "How is your day..", "Im ok.."]

        for word in commandL.split():
            if word in GREETING_INPUTS:
                telegram_bot.sendMessage (chat_id, random.choice(GREETING_RESPONSES)+"\n\nType /Help to see a list of commands..")
                return

        if '/help' in commandL:
            telegram_bot.sendMessage (chat_id, str("Use the following commands to interact with me:\n\n/Start - Enable all sensors to monitor activities and send updates.\n\n/Stop - Stop all sensor activities, you will no longer receive sensor messages.\n\n/Disable_Vibration_Sensor - Disable updates from vibration sensor.\n\n/Enable_Vibration_Sensor - Resume updates from vibration sensor.\n\n/Disable_Motion_Sensor - Disable updates from motion sensor.\n\n/Enable_Motion_Sensor - Resume updates from motion sensor.\n\n/Time - Report the system time.\n\n/Cam1_Pic - Take a picture from Cam1.\n\n/Cam2_Pic - Take a picture from Cam2.\n\n/Cam1_Video - Capture 10 Sec video from Cam1.\n\n/Cam2_Video - Capture 10 Sec video from Cam2.\n\n/Use_Pic - Send images on sensor triggers for all cameras.\n\n/Use_Pic_Cam1- Send images on sensor triggers for Cam1 only.\n\n/Use_Pic_Cam2- Send images on sensor triggers for Cam2 only.\n\n/Use_Video - Send videos on sensor triggers for all cameras.\n\n/Use_Video_Cam1- Send videos on sensor triggers for Cam1 only.\n\n/Use_Video_Cam2 - Send videos on sensor triggers for Cam2 only.\n\n/Show_ip - Show the local IP address.\n\n/Temperature - Check system temperature.\n\n/Disk_Space - Check the space usage on the SD card\n\n/Reboot - Reboot the device.\n\n/Shutdown - Turn off the device."))
            pass
        elif commandL == '/time':
            telegram_bot.sendMessage(chat_id, str(now.hour)+str(":")+str(now.minute))
            pass
        elif '/disable_message_' in commandL:
            localID = commandS[2]
            response = updateRegister(1,localID,0,'sendAlert')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'Message update from '+sensorName+' ['+localID+'] has been disabled!!'
            elif state == 'A':
              msg = 'Message update from '+sensorName+' ['+localID+'] is already disabled!!'
            elif state == '0':
              msg = localID+' isn\'t registered, please confirm the ID and try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/enable_message_' in commandL:
            localID = commandS[2]
            response = updateRegister(1,localID,1,'sendAlert')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'Message update from '+sensorName+' ['+localID+'] has been enabled!!'
            elif state == 'A':
              msg = 'Message update from '+sensorName+' ['+localID+'] is already enabled!!'
            elif state == '0':
              msg = localID+' isn\'t registered, please confirm the ID and try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/disable_sms_' in commandL:
            localID = commandS[2]
            response = updateRegister(1,localID,0,'sendSms')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'SMS update from '+sensorName+' ['+localID+'] has been disabled!!'
            elif state == 'A':
              msg = 'SMS update from '+sensorName+' ['+localID+'] is already disabled!!'
            elif state == '0':
              msg = localID+' isn\'t registered, please confirm the ID and try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/enable_sms_' in commandL:
            localID = commandS[2]
            response = updateRegister(1,localID,1,'sendSms')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'SMS update from '+sensorName+' ['+localID+'] has been enabled!!'
            elif state == 'A':
              msg = 'SMS update from '+sensorName+' ['+localID+'] is already enabled!!'
            elif state == '0':
              msg = localID+' isn\'t registered, please confirm the ID and try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/disable_media_' in commandL:
            localID = commandS[2]
            response = updateRegister(1,localID,0,'useCam')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'Media update from '+sensorName+' ['+localID+'] has been disabled!!'
            elif state == 'A':
              msg = 'Media update from '+sensorName+' ['+localID+'] is already disabled!!'
            elif state == '0':
              msg = localID+' isn\'t registered, please confirm the ID and try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/enable_media_' in commandL:
            localID = commandS[2]
            response = updateRegister(1,localID,1,'useCam')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'Media update from '+sensorName+' ['+localID+'] has been enabled!!'
            elif state == 'A':
              msg = 'Media update from '+sensorName+' ['+localID+'] is already enabled!!'
            elif state == '0':
              msg = localID+' isn\'t registered, please confirm the ID and try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif 'use_media_' in commandL:
            try:
              media = commandS[2]
              localID = commandS[3]
            except Exception as e:
              media = '0'
            if media.lower() == 'video':
              response = updateRegister(1,localID,'v','iOrv')
              state = response[0]
              sensorName = response[1]
              vidLength = response[2]
              camType = response[3]
              camIP = response[4]
              if state == '1':
                if camType == 'ipcam':
                  msg = sensorName+' ['+localID+'] will send '+str(vidLength)+' Sec videos from '+camType+' '+camIP+' on sensor trigger!!'
                else:
                  msg = sensorName+' ['+localID+'] will send '+str(vidLength)+' Sec videos from '+camType+' on sensor trigger!!'
              elif state == 'A':
                if camType == 'ipcam':
                  msg = sensorName+' ['+localID+'] is already configured to send videos from '+camType+' '+camIP+' on sensor trigger!!'
                else:
                  msg = sensorName+' ['+localID+'] is already configured to send videos from '+camType+' on sensor trigger!!'
              elif state == '0':
                msg = 'Please confirm the ID and try again, you entered: \''+localID+'\' as your sensorID'
              else:
                msg = 'Operation failed, please try again..'
            elif media.lower() == 'image':
              response = updateRegister(1,localID,'i','iOrv')
              state = response[0]
              sensorName = response[1]
              camType = response[3]
              camIP = response[4]
              if state == '1':
                if camType == 'ipcam':
                  msg = sensorName+' ['+localID+'] will send images from '+camType+' '+camIP+' on sensor trigger!!'
                else:
                  msg = sensorName+' ['+localID+'] will send images from '+camType+' on sensor trigger!!'
              elif state == 'A':
                if camType == 'ipcam':
                  msg = sensorName+' ['+localID+'] is already configured to send images from '+camType+' '+camIP+' on sensor trigger!!'
                else:
                  msg = sensorName+' ['+localID+'] is already configured to send images from '+camType+' on sensor trigger!!'
              elif state == '0':
                msg = 'Please confirm the ID and try again, you entered: \''+localID+'\' as your sensorID'
              else:
                msg = 'Operation failed, please try again..'
            else:
              msg = 'Please specify either image or video and sensorID in your syntax. \n The correct syntax is \'/use_media_video_SensorID\' or \'/use_media_image_SensorID\''
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/set_videolength_' in commandL:
            try:
              length = commandS[2]
              localID = commandS[3]
              error = 0
            except Exception as e:
              error = 1
            if error == 0:
              try:
                len = int(length)
                error = 0
              except Exception as e:
                error = 1
              if error == 0:
                if int(length) > 3 and int(length) < 60:
                  response = updateRegister(1,localID,str(length),'vidLength')
                  state = response[0]
                  sensorName = response[1]
                  vidLength = response[2]
                  camType = response[3]
                  camIP = response[4]
                  if state == '1':
                    if camType == 'ipcam':
                      msg = sensorName+' ['+localID+'] will send '+str(length)+' Sec videos from '+camType+' '+camIP+' on sensor trigger when video mode is selected!!'
                    else:
                      msg = sensorName+' ['+localID+'] will send '+str(length)+' Sec videos from '+camType+' on sensor trigger when video mode is selected!!'
                  elif state == 'A':
                    if camType == 'ipcam':
                      msg = sensorName+' ['+localID+'] is already configured to send '+str(length)+' Sec videos from '+camType+' '+camIP+' on sensor trigger if video mode is selected!!'
                    else:
                      msg = sensorName+' ['+localID+'] is already configured to send '+str(length)+' Sec videos from '+camType+' on sensor trigger if video mode is selected!!'
                  elif state == '0':
                    msg = 'Please confirm the ID and try again, you entered: \''+localID+'\' as your sensorID'
                  else:
                    msg = 'Operation failed, please try again..'
                else:
                  msg = 'Please enter video length between 3 and 60 Seconds. \nThe correct syntax is: \n\'/set_videolength_seconds_SensorID'
              else:
                msg = 'Please enter a valid number between 3 and 60 as the video length..'
            else:
              msg = 'Use the correct syntax and try again. \nThe correct syntax is \'/Set_videolength_seconds_SensorID\''
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/use_camera_' in commandL:
            try:
              cam = commandS[2]
              localID = commandS[3]
              error = 0
            except Exception as e:
              print e
              error = 1
            if error == 0:
              if cam == 'ipcam':
                try:
                  ipAddr = commandS[4]
                  error = 0
                except Exception as e:
                  print e
                  error = 1
                if error == 0:
                  validIP = validate_ip(ipAddr)
                  if validIP == True:
                    response = updateRegister(2,localID,cam,'camType',ipAddr,'camIP')
                    state = response[0]
                    sensorName = response[1]
                    if state == '1':
                      msg = sensorName+' ['+localID+'] will use '+cam+' '+ipAddr+' for videos and images'
                    elif state == 'A':
                      msg = sensorName+' ['+localID+'] is already configured to use '+cam+' '+ipAddr+' for videos and images'
                    elif state == '0':
                      msg = localID+' isn\'t registered, please confirm the ID and try again..'
                    else:
                      msg = 'Operation failed, please try again..'
                  else:
                    msg = 'You have entered an invalid IP Address, check the IP Address and try again..'
                else:
                  msg = 'Please provide an IP address. The correct syntax is: \nThe correct syntax is \'/Use_camera_cameratype_SensorID_ipaddress\''
              elif cam == 'usbcam' or cam == 'picam':
                response = updateRegister(1,localID,cam,'camType')
                state = response[0]
                sensorName = response[1]
                if state == '1':
                  msg = sensorName+' ['+localID+'] will use '+cam+' for videos and images'
                elif state == 'A':
                  msg = sensorName+' ['+localID+'] is already configured to use '+cam+' for videos and images'
                elif state == '0':
                  msg = localID+' isn\'t registered, please confirm the ID and try again..'
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = 'Please enter a valid camera type. \nThe correct syntax is \'/Use_camera_cameratype_SensorID_ipaddress\' \nWhere cameratype is either: usbcam, picam or ipcam.\nIf camera type is ipcam you have to type its ip address in the ipaddress section.'
            else:
              msg = 'Please use the correct syntax and try again. \nThe correct syntax is \'/Use_camera_cameratype_SensorID_ipaddress\' \nWhere cameratype is either: usbcam, picam or ipcam.\nIf camera type is ipcam you have to type its ip address in the ipaddress section.'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/cam1_pic' in commandL:
            telegram_bot.sendMessage(chat_id, str("Capturing Cam1 Image.."))
            output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takePiCamImg.sh", "/home/pi/Watchman/Images/picamimg.jpg"])
            telegram_bot.sendPhoto (chat_id, photo=open('/home/pi/Watchman/Images/picamimg.jpg'))
        elif '/cam1_video' in commandL:
            telegram_bot.sendMessage(chat_id, str("Capturing 10 Sec Cam1 Video.."))
            output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Videos/picamvid.mp4"])
            output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takePiCamVid.sh", "/home/pi/Watchman/Videos/picamvid.mp4", "10000"])
            telegram_bot.sendVideo (chat_id, video=open('/home/pi/Watchman/Videos/picamvid.mp4'))
        elif '/cam2_pic' in commandL:
            telegram_bot.sendMessage(chat_id, str("Capturing Cam2 Image.."))
            output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takeUSB1CamImg.sh", "/home/pi/Watchman/Images/usb1camimg.jpg"])
            telegram_bot.sendPhoto (chat_id, photo=open('/home/pi/Watchman/Images/usb1camimg.jpg'))
        elif '/cam2_video' in commandL:
            telegram_bot.sendMessage(chat_id, str("Capturing 10 Sec Cam2 Video.."))
            output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Videos/usb1camvid.avi"])
            output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takeUSB1CamVid.sh", "/home/pi/Watchman/Videos/usb1camvid.avi", "10"])
            telegram_bot.sendVideo (chat_id, video=open('/home/pi/Watchman/Videos/usb1camvid.avi'))
        elif commandL == '/stop':
            m = open("/home/pi/Watchman/allowToSendMotionMsg.txt","w+")
            m.write('0')
            m.close()
            v = open("/home/pi/Watchman/allowToSendVibMsg.txt","w+")
            v.write('0')
            v.close()
            telegram_bot.sendMessage (chat_id, str("All sensor have been disabled!!\nSend /Start to enable them.."))
        elif commandL == '/start':
            m = open("/home/pi/Watchman/allowToSendMotionMsg.txt","w+")
            m.write('1')
            m.close()
            v = open("/home/pi/Watchman/allowToSendVibMsg.txt","w+")
            v.write('1')
            v.close()
            telegram_bot.sendMessage (chat_id, str("All sensors have been enabled!!\nSend /Stop to disable them.."))
        elif commandL == '/temperature':
            t=float(subprocess.check_output(["/opt/vc/bin/vcgencmd measure_temp | cut -c6-9"], shell=True)[:-1])
            ts=str(t)
            answer = 'My temperature is '+ts+' °C'
            telegram_bot.sendMessage (chat_id, str(answer))
        elif commandL == '/show_ip':
            ip_address = '';
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8",80))
            ip_address = s.getsockname()[0]
            s.close()
            #ssid = subprocess.check_output(["iwgetid"])
            #msg = "Connected to:\n"+ssid+"\nLocal IP Address:\n"+ip_address
            msg = "Local IP Address:\n"+ip_address
            telegram_bot.sendMessage (chat_id, str(msg))
        elif '/disk_space' in commandL:
            result=subprocess.check_output("df -h .", shell=True)
            output=result.split()
            answer = "Disk space\nTotal: "+output[8]+"\nUsed: "+output[9]+" ("+output[11]+")\nFree: "+output[10]
            telegram_bot.sendMessage (chat_id, str(answer))
        elif commandL == '/reboot':
            telegram_bot.sendMessage (chat_id, str("System will reboot after 1 minute.."))
            output = subprocess.Popen(["sudo", "shutdown", "-r"])
        elif commandL == '/shutdown':
            telegram_bot.sendMessage (chat_id, str("System will shutdown after 1 minute..\n\nSwitch off power supply after shutdown, Switch on power supply to turn on the system again."))
            output = subprocess.Popen(["sudo", "shutdown"])
        else:
            answer = "Sorry "+username+", I can't understand what you're asking me, try typing '/Help'."
            telegram_bot.sendMessage (chat_id, str(answer))

c = open("/home/pi/Watchman/TelegramBot/isBotRunning.txt","r")
status = c.read()
status = status.strip()
c.close()
if status == '1':
    ts = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    print '['+ts + '] bot already running!!'
    exit()

t = open("/home/pi/Watchman/TelegramBot/token.txt","r")
token = t.read()
t.close()
token = token.strip()

telegram_bot = telepot.Bot(token)
print (telegram_bot.getMe())

MessageLoop(telegram_bot, action).run_as_thread()
ts = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+'] Up and Running....'
c = open("/home/pi/Watchman/TelegramBot/isBotRunning.txt","w+")
status = c.write('1')
c.close()

try:
    while 1:
        time.sleep(10)
except:
    ts = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    print '['+ts+'] Bot is about to die..'
    c = open("/home/pi/Watchman/TelegramBot/isBotRunning.txt","w+")
    status = c.write('0')
    c.close()

