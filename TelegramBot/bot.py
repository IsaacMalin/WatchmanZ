#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
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
    if numOfValues == 0:
      cursor1.execute("SELECT * FROM registeredSensors")
    else:
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
          elif numOfValues == 0:
            cursor2.execute("UPDATE registeredSensors SET %s = '%s'"%(str(column1),str(value1)))
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

def validate_vid_length(time,minTime, maxTime):
    if not time.isdigit():
        return False
    len = int(time)
    if len < minTime or len > maxTime:
        return False
    return True

def validate_nodeID(id):
    if not id.isdigit():
        return False
    if int(id) < 1 or int(id) > 255:
        return False
    return True

def validate_localID(id):
    if len(id) != 6:
        return False
    numPart = id[3:6]
    if not numPart.isdigit():
        return False
    txtPart = id[0:3]
    if not txtPart.isalpha():
        return False
    return True

def validate_uniqueID(id):
    if not id.isdigit():
        return False
    return True

def validate_description(d):
    if len(d) < 2 or len(d) > 50:
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
            telegram_bot.sendMessage (chat_id, str("Use the following commands to interact with me:\n\n/Start - Enable all sensors to send updates when triggered.\n\n/Stop - Stop all sensor message updates.\n\n/Show_registered_sensors - Show all registered sensors.\n\n/Register_sensor_nodeID_localID_globalID_description - Register a new sensor.\n\n/Remove_sensor_SensorID - Unregister a sensor.\n\n/Show_configuration_SensorID - Show the configuration of your sensor.\n\n/Enable_message_SensorID - Enable message updates from your sensor.\n\n/Disable_message_SensorID - Disable alerts from your sensor.\n\n/Enable_media_SensorID - Enable media alerts(photo or video) when sensor is triggered.\n\n/Disable_media_SensorID - Disable photo and video messages when sensor is triggered.\n\n/Enable_sms_SensorID - Enable your sensor to send SMS message when Internet is unavailable.\n\n/Disable_sms_SensorID - Disable SMS alerts from your sensor.\n\n/Use_media_video_SensorID or \n/Use_media_image_SensorID - Configure your sensor to send either photos or videos when triggered.\n\n/Use_camera_cameratype_SensorID_ipaddress - Configure the type of camera your sensor will use when triggered.\n\n/Set_videolength_seconds_SensorID - Configure video clip duration when video mode is selected.\n\n/Capture_media_cameratype_seconds_ipaddress - Capture an image or video from your camera.\n\n/Temperature - Check system temperature.\n\n/Disk_Space - Check space usage on the SD card\n\n/Reboot - Reboot the device.\n\n/Shutdown - Turn off the device."))
            pass
        elif commandL == '/time':
            telegram_bot.sendMessage(chat_id, str(now.hour)+str(":")+str(now.minute))
            pass
        elif '/disable_message_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
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
            else:
              msg = "Please provide a valid ID. The correct format is: \n'/Disable_message_localID' \nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/enable_message_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
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
            else:
              msg = "Please provide a valid ID. The correct format is \n'/Enable_message_localID' \nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/disable_sms_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
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
            else:
              msg = "Please provide a valid ID. The correct format is \n'/Disable_sms_localID' \nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/enable_sms_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
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
            else:
              msg = "Please provide a valid ID. The correct format is \n'/Enable_sms_localID' \nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/disable_media_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
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
            else:
              msg = "Please provide a valid ID. The correct format is \n'/Disable_media_localID' \nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/enable_media_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
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
            else:
              msg = "Please provide a valid ID. The correct format is \n'/Enable_media_localID' \nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif 'use_media_' in commandL:
            try:
              media = commandS[2]
              localID = commandS[3]
            except Exception as e:
              media = '0'
            if media.lower() == 'video':
              if validate_localID(localID):
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
              else:
                msg = 'Please provide a valid ID. The correct format is: \n\'/Use_media_video_localID\' or \n/Use_media_image_localID \nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            elif media.lower() == 'image':
              if validate_localID(localID):
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
                msg = 'Please provide a valid ID. The correct format is: \n\'/Use_media_video_localID\' or \n/Use_media_image_localID \nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            else:
              msg = 'Please specify either image or video and sensor ID in your syntax. \n The correct format is \n\'/Use_media_video_localID\' or \n\'/Use_media_image_localID\' \nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
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
              minTime = 3
              maxTime = 60
              lengthValid = validate_vid_length(length,minTime, maxTime)
              if lengthValid == True:
                if validate_localID(localID):
                  response = updateRegister(1,localID,str(length),'vidLength')
                  state = response[0]
                  sensorName = response[1]
                  vidLength = response[2]
                  camType = response[3]
                  camIP = response[4]
                  if state == '1':
                    if camType.lower() == 'ipcam':
                      msg = sensorName+' ['+localID+'] will send '+str(length)+' Sec videos from '+camType+' '+camIP+' on sensor trigger when video mode is selected!!'
                    else:
                      msg = sensorName+' ['+localID+'] will send '+str(length)+' Sec videos from '+camType+' on sensor trigger when video mode is selected!!'
                  elif state == 'A':
                    if camType.lower() == 'ipcam':
                      msg = sensorName+' ['+localID+'] is already configured to send '+str(length)+' Sec videos from '+camType+' '+camIP+' on sensor trigger if video mode is selected!!'
                    else:
                      msg = sensorName+' ['+localID+'] is already configured to send '+str(length)+' Sec videos from '+camType+' on sensor trigger if video mode is selected!!'
                  elif state == '0':
                    msg = 'That ID is not registered.Please confirm the ID and try again, you entered: \''+localID+'\' as your sensorID'
                  else:
                    msg = 'Operation failed, please try again..'
                else:
                  msg = "Please provide a valid ID. \nThe correct format is: \n\n\'/Set_videolength_seconds_localID\' \n\nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
              else:
                msg = 'Please enter a valid number between '+str(minTime)+' and '+str(maxTime)+' as the video length.\nThe correct format is: \n\n\'/Set_videolength_seconds_localID\' \n\nWhere \'seconds\' is the video length in seconds and \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            else:
              msg = 'Use the correct syntax and try again. \nThe correct format is: \n\n\'/Set_videolength_seconds_localID\' \n\nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
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
              if validate_localID(localID):
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
                      msg = 'You have entered an invalid IP Address \''+str(ipAddr)+'\', check the IP Address and try again..'
                  else:
                    msg = 'Please provide an IP address. The correct format is: \n\n\'/Use_camera_cameratype_localID_ipaddress\''
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
                  msg = 'Please enter a valid camera type. \nThe correct format is: \n\n\'/Use_camera_cameratype_localID_ipaddress\' \n\nWhere cameratype is either: usbcam, picam or ipcam.\nIf camera type is ipcam you have to type its ip address in the ipaddress section.\n\'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
              else:
                msg = "Please provide a valid ID.  \nThe correct format is: \n\n'/Use_camera_cameratype_localID_ipaddress' \n\nWhere cameratype is either: usbcam, picam or ipcam.\nIf camera type is ipcam you have to type its ip address in the ipaddress section.\n'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            else:
              msg = 'Please use the correct syntax and try again. \nThe correct format is: \n\n\'/Use_camera_cameratype_localID_ipaddress\' \n\nWhere cameratype is either: usbcam, picam or ipcam.\nIf camera type is ipcam you have to type its ip address in the ipaddress section.\n\'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/capture_' in commandL:
            msg = 'Done!'
            try:
              media = commandS[1]
              camType = commandS[2]
              error = 0
            except Exception as e:
              error = 1
              print e
            if error == 0:
              if media.lower() == 'video':
                try:
                  seconds = commandS[3]
                except Exception as e:
                  error = 1
                  print e
                if error == 0:
                  minTime = 5
                  maxTime = 60
                  lengthValid = validate_vid_length(seconds,minTime, maxTime)
                  if lengthValid == True:
                    if camType.lower() == 'ipcam':
                      try:
                        ipAddr = commandS[4]
                        error = 0
                      except Exception as e:
                        print e
                        error = 1
                      if error == 0:
                        validIP = validate_ip(ipAddr)
                        if validIP == True:
                          telegram_bot.sendMessage(chat_id, str("Attempting to capture "+str(seconds)+" Sec video from IP camera - "+str(ipAddr)))
                          output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Videos/ipcamvid.mp4"])
                          output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takeIpCamVid.sh", "/home/pi/Watchman/Videos/ipcamvid.mp4", str(int(seconds)), str(ipAddr)])
                          fileExists = os.path.exists('/home/pi/Watchman/Videos/ipcamvid.mp4')
                          if fileExists == True:
                            telegram_bot.sendMessage(chat_id, str("Captured "+str(seconds)+" Sec video from IP camera - "+str(ipAddr)+", trying to send video.."))
                            telegram_bot.sendVideo (chat_id, video=open('/home/pi/Watchman/Videos/ipcamvid.mp4'))
                          else:
                            telegram_bot.sendMessage(chat_id, str("Video capture from IP camera - "+str(ipAddr)+" unsuccessful, please ensure ip camera is functioning and retry."))
                        else:
                          msg = 'Please provide a valid IP Address. \''+str(ipAddr)+'\' is not a valid ip address.'
                      else:
                        msg = 'Please provide an IP Address. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
                    elif camType.lower() == 'usbcam':
                      telegram_bot.sendMessage(chat_id, str("Attempting to capture "+str(seconds)+" Sec video from USB camera.."))
                      output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Videos/usb1camvid.avi"])
                      output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takeUSB1CamVid.sh", "/home/pi/Watchman/Videos/usb1camvid.avi", str(seconds)])
                      fileExists = os.path.exists('/home/pi/Watchman/Videos/usb1camvid.avi')
                      if fileExists == True:
                        telegram_bot.sendMessage(chat_id, str("Captured "+str(seconds)+" Sec video from USB camera, trying to send video.."))
                        telegram_bot.sendVideo (chat_id, video=open('/home/pi/Watchman/Videos/usb1camvid.avi'))
                      else:
                        telegram_bot.sendMessage(chat_id, str("Video capture from USB camera unsuccessful, please make sure camera is available and retry.."))
                    elif camType.lower() == 'picam':
                      telegram_bot.sendMessage(chat_id, str("Attempting to capture "+str(seconds)+" Sec video from Raspberry Pi camera.."))
                      output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Videos/picamvid.mp4"])
                      output = subprocess.call(["sudo", "/home/pi/Watchman/Videos/takePiCamVid.sh", "/home/pi/Watchman/Videos/picamvid.mp4", str(int(seconds)*1000)])
                      fileExists = os.path.exists('/home/pi/Watchman/Videos/picamvid.mp4')
                      if fileExists == True:
                        telegram_bot.sendMessage(chat_id, str("Captured "+str(seconds)+" Sec video from Raspberry Pi camera, trying to send video.."))
                        telegram_bot.sendVideo (chat_id, video=open('/home/pi/Watchman/Videos/picamvid.mp4'))
                      else:
                        telegram_bot.sendMessage(chat_id, str("Video capture from Raspberry Pi camera unsuccessful, please ensure pi camera is installed properly and retry."))
                    else:
                      msg = 'Please select the right camera type. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
                  else:
                    msg = 'Please enter a valid number between '+str(minTime)+' and '+str(maxTime)+' as the video length. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
                else:
                  msg = 'Please specify a camera type and the number of seconds you want for video. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
              elif media.lower() == 'image':
                if camType.lower() == 'ipcam':
                  try:
                    ipAddr = commandS[3]
                    error = 0
                  except Exception as e:
                    print e
                    error = 1
                  if error == 0:
                    validIP = validate_ip(ipAddr)
                    if validIP == True:
                      telegram_bot.sendMessage(chat_id, str("Attempting to capture a photo from IP camera - "+str(ipAddr)))
                      output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Images/ipcamimg.jpg"])
                      output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takeIpCamImg.sh", "/home/pi/Watchman/Images/ipcamimg.jpg", str(ipAddr)])
                      fileExists = os.path.exists('/home/pi/Watchman/Images/ipcamimg.jpg')
                      if fileExists == True:
                        telegram_bot.sendMessage(chat_id, str("Photo captured! trying to send it.."))
                        telegram_bot.sendPhoto (chat_id, photo=open('/home/pi/Watchman/Images/ipcamimg.jpg'))
                      else:
                        telegram_bot.sendMessage(chat_id, str("Photo capture from IP camera - "+str(ipAddr)+" unsuccessful, please ensure IP camera is functioning and retry."))
                    else:
                      msg = 'Please provide a valid IP Address. \''+str(ipAddr)+'\' is not a valid ip address.'
                  else:
                    msg = 'Please provide an IP Address. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
                elif camType.lower() == 'usbcam':
                  telegram_bot.sendMessage(chat_id, str("Attempting to capture a photo from USB camera.."))
                  output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Images/usb1camimg.jpg"])
                  output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takeUSB1CamImg.sh", "/home/pi/Watchman/Images/usb1camimg.jpg"])
                  fileExists = os.path.exists('/home/pi/Watchman/Images/usb1camimg.jpg')
                  if fileExists == True:
                    telegram_bot.sendMessage(chat_id, str("Photo captured! trying to send it.."))
                    telegram_bot.sendPhoto (chat_id, photo=open('/home/pi/Watchman/Images/usb1camimg.jpg'))
                  else:
                    telegram_bot.sendMessage(chat_id, str("Photo capture from USB camera unsuccessful, please make sure camera is available and retry.."))
                elif camType.lower() == 'picam':
                  telegram_bot.sendMessage(chat_id, str("Attempting to capture a photo from Raspberry Pi camera.."))
                  output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Images/picamimg.jpg"])
                  output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takePiCamImg.sh", "/home/pi/Watchman/Images/picamimg.jpg"])
                  fileExists = os.path.exists('/home/pi/Watchman/Images/picamimg.jpg')
                  if fileExists == True:
                    telegram_bot.sendMessage(chat_id, str("Photo captured! trying to send it.."))
                    telegram_bot.sendPhoto (chat_id, photo=open('/home/pi/Watchman/Images/picamimg.jpg'))
                  else:
                    telegram_bot.sendMessage(chat_id, str("Photo capture from Raspberry Pi camera unsuccessful, please ensure pi camera is installed properly and retry."))
                else:
                  msg = 'Please select the right camera type. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
                pass
              else:
                msg = 'You have entered an invalid media type, please type video or image as media type. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
            else:
              msg = 'Please provide media type you want to capture and camera type. The correct format is: \n\n\'/Capture_media_cameratype_seconds_ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/register_sensor_' in commandL:
            try:
              nodeID = commandS[2]
              localID = commandS[3]
              uniqueID = commandS[4]
              description = commandS[5]
              error = 0
            except Exception as e:
              error = 1
            if error == 0:
              if validate_nodeID(nodeID):
                 if validate_localID(localID):
                   if validate_uniqueID(uniqueID):
                     if validate_description(description):
                       if int(localID[3:6]) == int(nodeID):
                         regTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                         mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
                         cursor1 = mariadb_connection.cursor()
                         try:
                           cursor1.execute("INSERT INTO registeredSensors (nodeID,sensorName,localID,globalID,regDate) VALUES(%s,'%s','%s',%s,'%s')"%(str(nodeID),str(description),str(localID),str(uniqueID),str(regTime)))
                           rowCount = cursor1.rowcount
                           cursor1.close()
                           mariadb_connection.commit()
                           if rowCount >= 1:
                             msg = description+'['+localID+'] has been registered!!'
                           else:
                             msg = description+'['+localID+'] has not been registered!! confirm your entries and try again.'
                         except mariadb.Error as error:
                           print("Error: {}".format(error))
                           msg = 'Database error occurred. Make sure there is no other sensor registered with the same nodeID and try again..'
                         mariadb_connection.close()
                       else:
                         msg = 'nodeID should be the same number as the digit part of localID. e.g. if sensor address is VIB255-234567, localID is VIB255, nodeID should be typed as 255.'
                     else:
                       msg = 'Please provide a short description or name to identify your sensor. The correct format is: \n\n\'/Register_sensor_nodeID_localID_globalID_description\' \n\nWhere \'nodeID\' is the number in localID address e.g sensor address VIB001-234567 will have nodeID 1. \'localID\' is the first part of sensor address e.g VIB001. \'globalID\' is the second part of your sensor address e.g 234567. \'description \' is the name or description you give to identify your sensor e.g Front door vibration sensor'
                   else:
                     msg = 'Please type the correct globalID. If your sensor address is VIB001-234567 the globalID is 234567. The correct format is: \n\n\'/Register_sensor_nodeID_localID_globalID_description\' \n\nWhere \'nodeID\' is the number in localID address e.g sensor address VIB001-234567 will have nodeID 1. \'localID\' is the first part of sensor address e.g VIB001. \'globalID\' is the second part of your sensor address e.g 234567. \'description \' is the name or description you give to identify your sensor e.g Front door vibration sensor'
                 else:
                   msg = 'Please type the correct localID. If your sensor address is VIB001-234567 the localID is VIB001. The correct format is: \n\n\'/Register_sensor_nodeID_localID_globalID_description\' \n\nWhere \'nodeID\' is the number in localID address e.g sensor address VIB001-234567 will have nodeID 1. \'localID\' is the first part of sensor address e.g VIB001. \'globalID\' is the second part of your sensor address e.g 234567. \'description \' is the name or description you give to identify your sensor e.g Front door vibration sensor'
              else:
                msg = 'Please type the correct nodeID, it should be a number between 1 and 255. The correct format is: \n\n\'/Register_sensor_nodeID_localID_globalID_description\' \n\nWhere \'nodeID\' is the number in localID address e.g sensor address VIB001-234567 will have nodeID 1. \'localID\' is the first part of sensor address e.g VIB001. \'globalID\' is the second part of your sensor address e.g 234567. \'description \' is the name or description you give to identify your sensor e.g Front door vibration sensor.'
            else:
              msg = 'Sensor registration failed. Please use the correct format and fill in every section. The correct format is: \n\n\'/Register_sensor_nodeID_localID_globalID_description\' \n\nWhere \'nodeID\' is the number in localID address e.g sensor address VIB001-234567 will have nodeID 1. \'localID\' is the first part of sensor address e.g VIB001. \'globalID\' is the second part of your sensor address e.g 234567. \'description \' is the name or description you give to identify your sensor e.g Front door vibration sensor'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/remove_sensor_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
              mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
              cursor1 = mariadb_connection.cursor()
              try:
                cursor1.execute("SELECT * FROM registeredSensors WHERE localID = '%s'"%(localID))
                result = cursor1.fetchall()
                rowCount = len(result)
                cursor1.close()
                if rowCount >= 1:
                  for row in result:
                    sensorName = row[1]
                    cursor2 = mariadb_connection.cursor()
                    try:
                      cursor2.execute("DELETE FROM registeredSensors WHERE localID = '%s'"%(localID))
                      rowCount = cursor2.rowcount
                      cursor2.close()
                      mariadb_connection.commit()
                      if rowCount >= 1:
                        msg = sensorName+'['+localID+'] has been deleted'
                      else:
                        msg = 'Operation failed, please try again. The correct format is: \n\'/Remove_sensor_localID\' \nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
                    except mariadb.Error as error:
                      print("Error: {}".format(error))
                      msg = 'Database error occurred. Please retry later.'
                else:
                  msg = 'The localID \''+localID+'\' did not match any registered sensors. Please confirm your ID and try again..'
              except mariadb.Error as error:
                print("Error: {}".format(error))
                msg = 'Database error occurred. Please retry later.'
              mariadb_connection.close()
            else:
              msg = 'Please type in a valid ID. The correct format is: \n\'/Remove_sensor_localID\' \nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/show_configuration_' in commandL:
            localID = commandS[2]
            if validate_localID(localID):
              mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
              cursor1 = mariadb_connection.cursor()
              try:
                cursor1.execute("SELECT * FROM registeredSensors WHERE localID = '%s'"%(localID))
                result = cursor1.fetchall()
                rowCount = len(result)
                cursor1.close()
                if rowCount >= 1:
                  for row in result:
                    sensorName = row[1]
                    localID = row[2]
                    active = row[4]
                    lastSeen = row[5]
                    camType = row[7]
                    camIP = row[8]
                    media = row[9]
                    vidLength = row[10]
                    sendAlert = row[11]
                    sendSms = row[12]
                    useCam = row[13]
                    def checkActive(active):
                      if active != None:
                        if active == 1:
                          return 'Active'
                        else:
                          return 'Inactive'
                      else:
                        return 'Unknown'
                    def returnYesOrNo(alert):
                      if alert == 1:
                        return 'Yes'
                      else:
                        return 'No'
                    def checkMedia(media):
                      if media == 'i':
                        return 'Photo'
                      elif media == 'v':
                        return 'Video'
                      else:
                        return 'Unspecified'
                    def checkLastSeen(lastSeen):
                      if lastSeen != None:
                        return str(lastSeen)
                      else:
                        return 'Unknown'
                    def checkCamTypeOrIP(camTypeIP):
                      if camTypeIP != None:
                        return camTypeIP
                      else:
                        return 'Not specified'
                    msg = sensorName+"["+localID+"] \nconfiguration: \n\nStatus: "+checkActive(active)+" \n\nLast Seen :"+checkLastSeen(lastSeen)+" \n\nSend alert on trigger: "+returnYesOrNo(sendAlert)+" \n\nSend SMS alerts: "+returnYesOrNo(sendSms)+" \n\nSend media on trigger: "+returnYesOrNo(useCam)+" \n\nUse camera type: "+checkCamTypeOrIP(camType)+"\n\nIP Camera address: "+checkCamTypeOrIP(camIP)+" \n\nUse media: "+checkMedia(media)+" \n\nVideo length for video mode: "+str(vidLength)
                else:
                  msg = 'There is no sensor registered as \''+localID+'\'.'
              except mariadb.Error as error:
                print("Error: {}".format(error))
                msg = 'Database error occurred. Please retry later.'
              mariadb_connection.close()
            else:
              msg = 'Please type a valid ID. The correct format is: \n\'/Show_configuration_localID\' \nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            telegram_bot.sendMessage(chat_id, str(msg))
        elif '/show_registered_sensors' in commandL:
            mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')
            cursor1 = mariadb_connection.cursor()
            try:
              cursor1.execute("SELECT * FROM registeredSensors")
              result = cursor1.fetchall()
              rowCount = len(result)
              cursor1.close()
              if rowCount >= 1:
                msg = 'Registered Sensors:'
                count = 0
                for row in result:
                  count += 1
                  sensorName = row[1]
                  localID = row[2]
                  active = row[4]
                  lastSeen = row[5]
                  camType = row[7]
                  camIP = row[8]
                  media = row[9]
                  vidLength = row[10]
                  sendAlert = row[11]
                  sendSms = row[12]
                  useCam = row[13]
                  if active == 1:
                    if lastSeen != None:
                      msg += '\n\n'+str(count)+'. ['+localID+'][Active] '+sensorName+'. Last seen: '+str(lastSeen)
                    else:
                      msg += '\n\n'+str(count)+'. ['+localID+'][Active] '+sensorName+'.'
                  else:
                    if lastSeen != None:
                      msg += '\n\n'+str(count)+'. ['+localID+'][Inactive] '+sensorName+'. Last seen: '+str(lastSeen)
                    else:
                      msg += '\n\n'+str(count)+'. ['+localID+'][Inactive] '+sensorName+'.'
              else:
                msg = 'You have no registered sensors!!'
            except mariadb.Error as error:
              print("Error: {}".format(error))
              msg = 'Database error occurred. Please retry later.'
            mariadb_connection.close()
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif commandL == '/stop':
            response = updateRegister(0,'*',0,'sendAlert')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'Message update from all sensors have been disabled, you will no longer receive any updates. \nType /Start to enable updates from sensors.'
            elif state == 'A':
              msg = 'Message update from all sensors have already been disabled, you will no longer receive any updates. \nType /Start to enable updates from sensors.'
            elif state == '0':
              msg = 'There was an error, have you registered any sensors? please try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif commandL == '/start':
            response = updateRegister(0,'*',1,'sendAlert')
            state = response[0]
            sensorName = response[1]
            if state == '1':
              msg = 'Message update from all sensors have been enabled, you will receive updates from all sensors. \nType /Stop to disable updates from all sensors.'
            elif state == 'A':
              msg = 'Message update from all sensors have already been enabled, you will receive updates from all sensors. \nType /Stop to disable updates from all sensors.'
            elif state == '0':
              msg = 'There was an error, have you registered any sensors? please try again..'
            else:
              msg = 'Operation failed, please try again..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif commandL == '/temperature':
            t=float(subprocess.check_output(["/opt/vc/bin/vcgencmd measure_temp | cut -c6-9"], shell=True)[:-1])
            ts=str(t)
            answer = 'My temperature is '+ts+' °C'
            telegram_bot.sendMessage (chat_id, str(answer))
            pass
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
            pass
        elif '/disk_space' in commandL:
            result=subprocess.check_output("df -h .", shell=True)
            output=result.split()
            answer = "Disk space\nTotal: "+output[8]+"\nUsed: "+output[9]+" ("+output[11]+")\nFree: "+output[10]
            telegram_bot.sendMessage (chat_id, str(answer))
            pass
        elif commandL == '/reboot':
            telegram_bot.sendMessage (chat_id, str("System will reboot after 1 minute.."))
            output = subprocess.Popen(["sudo", "shutdown", "-r"])
            pass
        elif commandL == '/shutdown':
            telegram_bot.sendMessage (chat_id, str("System will shutdown after 1 minute..\n\nSwitch off power supply after shutdown, Switch on power supply to turn on the system again."))
            output = subprocess.Popen(["sudo", "shutdown"])
            pass
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

