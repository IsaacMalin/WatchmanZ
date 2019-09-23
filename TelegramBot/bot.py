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
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('/home/pi/Watchman/WatchmanConfig.ini')
chat_id = config.get('ConfigVariables', 'chatid')
token = config.get('ConfigVariables', 'token')

now = datetime.datetime.now()

config2 = SafeConfigParser()
config2.read('/home/pi/Watchman/sqldb/sqlCredentials.ini')

usr = config2.get('credentials', 'username')
pswd = config2.get('credentials', 'password')
db = config2.get('credentials', 'database')

def updateNRFRegister(numOfValues,localID,value1,column1,value2=None,column2=None,value3=None,column3=None,value4=None,column4=None):
  mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
  cursor1 = mariadb_connection.cursor()
  try:
    if numOfValues == 0:
      cursor1.execute("SELECT * FROM registeredNRFSensors")
    else:
      cursor1.execute("SELECT * FROM registeredNRFSensors WHERE localID = '%s'"%(str(localID)))
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
            cursor2.execute("UPDATE registeredNRFSensors SET %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(localID)))
          elif numOfValues == 2:
            cursor2.execute("UPDATE registeredNRFSensors SET %s = '%s', %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(localID)))
          elif numOfValues == 3:
            cursor2.execute("UPDATE registeredNRFSensors SET %s = '%s', %s = '%s', %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(column3),str(value3),str(localID)))
          elif numOfValues == 4:
            cursor2.execute("UPDATE registeredNRFSensors SET %s = '%s', %s = '%s', %s = '%s', %s = '%s' WHERE localID = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(column3),str(value3),str(column4),str(value4),str(localID)))
          elif numOfValues == 0:
            cursor2.execute("UPDATE registeredNRFSensors SET %s = '%s'"%(str(column1),str(value1)))
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

def updateWifiRegister(numOfValues,ip,value1,column1,value2=None,column2=None,value3=None,column3=None,value4=None,column4=None):
  mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
  cursor1 = mariadb_connection.cursor()
  try:
    if numOfValues == 0:
      cursor1.execute("SELECT * FROM registeredWifiSensors")
    else:
      cursor1.execute("SELECT * FROM registeredWifiSensors WHERE ip = '%s'"%(str(ip)))
    result = cursor1.fetchall()
    rowCount = len(result)
    cursor1.close()
    #print rowCount
    if rowCount >= 1:
      for row in result:
        sensorName = row[1]
        vidLength = row[8]
        camType = row[5]
        camIP = row[6]
        cursor2 = mariadb_connection.cursor()
        try:
          if numOfValues == 1:
            cursor2.execute("UPDATE registeredWifiSensors SET %s = '%s' WHERE IP = '%s'"%(str(column1),str(value1),str(ip)))
          elif numOfValues == 2:
            cursor2.execute("UPDATE registeredWifiSensors SET %s = '%s', %s = '%s' WHERE IP = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(ip)))
          elif numOfValues == 3:
            cursor2.execute("UPDATE registeredWifiSensors SET %s = '%s', %s = '%s', %s = '%s' WHERE IP = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(column3),str(value3),str(ip)))
          elif numOfValues == 4:
            cursor2.execute("UPDATE registeredWifiSensors SET %s = '%s', %s = '%s', %s = '%s', %s = '%s' WHERE IP = '%s'"%(str(column1),str(value1),str(column2),str(value2),str(column3),str(value3),str(column4),str(value4),str(ip)))
          elif numOfValues == 0:
            cursor2.execute("UPDATE registeredWifiSensors SET %s = '%s'"%(str(column1),str(value1)))
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
    config.read('/home/pi/Watchman/WatchmanConfig.ini')
    authorizedUser = config.get('ConfigVariables', 'username')

    if username == authorizedUser:

        configS = SafeConfigParser()
        configS.read('/home/pi/Watchman/WatchmanConfig.ini')
        configS.set('ConfigVariables','chatid', str(chat_id))
        with open('/home/pi/Watchman/WatchmanConfig.ini', 'w') as configfile:
          configS.write(configfile)

        command = msg['text']
        commandL = command.lower()
        commandC = command.replace(" ","")
        commandS = commandC.split("|")
        commandS2 = command.split("|")

        ts = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        print '['+ts+'] Received: %s' % command

        GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey", "wasup", "sasa", "bonjour", "howdy", "how are you", "vipi")
        GREETING_RESPONSES = ["Hi, ", "Hey, ", "Hello, ", "Hi there, ", "How is your day, "]

        for word in commandL.split():
            if word in GREETING_INPUTS:
                telegram_bot.sendMessage (chat_id, random.choice(GREETING_RESPONSES)+"type /Help to see a list of commands..")
                return

        if '/help' in commandL:
            telegram_bot.sendMessage (chat_id, str("Use the following commands to configure your device:\n/Start\n/Stop\n/Show_NRF_sensor_commands\n/Show_IP_sensor_commands\n/Show_camera_commands\n/Disable_gprs\n/Temperature\n/Disk_Space\n/Reboot\n/Shutdown"))
            pass
        elif '/show_nrf_sensor_commands' in commandL:
            telegram_bot.sendMessage (chat_id, str("NRF-Sensor Configuration Commands:\n\n/NRF_show_registered_sensors\n\n/NRF_show_configuration|SensorID\n\n/NRF_register_sensor|nodeID|localID|globalID|description\n\n/NRF_remove_sensor|SensorID\n\n/NRF_enable_message|SensorID\n\n/NRF_disable_message|SensorID\n\n/NRF_enable_media|SensorID\n\n/NRF_disable_media|SensorID\n\n/NRF_enable_sms|SensorID\n\n/NRF_disable_sms|SensorID\n\n/NRF_use_media|mediatype|SensorID\n\n/NRF_use_camera|cameratype|SensorID|ipaddress\n\n/NRF_set_videolength|seconds|SensorID"))
            pass
        elif '/show_ip_sensor_commands' in commandL:
            telegram_bot.sendMessage (chat_id, str("IP-Sensor Configuration Commands:\n\n/IP_show_registered_sensors\n\n/IP_show_configuration|ipaddress\n\n/IP_register_sensor|ipaddress|description\n\n/IP_remove_sensor|ipaddress\n\n/IP_enable_message|ipaddress\n\n/IP_disable_message|ipaddress\n\n/IP_enable_media|ipaddress\n\n/IP_disable_media|ipaddress\n\n/IP_enable_sms|ipaddress\n\n/IP_disable_sms|ipaddress\n\n/IP_use_media|mediatype|ipaddress\n\n/IP_use_camera|cameratype|sensoripaddress|cameraipaddress\n\n/IP_set_videolength|seconds|ipaddress"))
            pass
        elif '/show_camera_commands' in commandL:
            telegram_bot.sendMessage (chat_id, str("Camera Configuration Commands:\n\n/Capture|mediatype|cameratype|seconds|ipaddress\n\n/Show_available_camera\n\n/IPCam_register_camera|ipaddress|description\n\n/IPCam_remove_camera|ipaddress"))
            pass
        elif commandL == '/time':
            telegram_bot.sendMessage(chat_id, str(now.hour)+str(":")+str(now.minute))
            pass
        elif '/nrf_disable_message' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/NRF_disable_message | localID\' \n\nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            if error == 0:
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,0,'sendAlert')
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
                msg = "Please provide a valid ID."+correctFmt
            else:
              msg = "Please type in your sensor-localID."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_disable_message' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/IP_disable_message | ipaddress\' \n\nWhere \'ipaddress\' is the IP Address assigned to your WiFi Sensor.'
            if error == 0:
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,0,'sendAlert')
                state = response[0]
                sensorName = response[1]
                if state == '1':
                  msg = 'Message update from '+sensorName+' ['+ip+'] has been disabled!!'
                elif state == 'A':
                  msg = 'Message update from '+sensorName+' ['+ip+'] is already disabled!!'
                elif state == '0':
                  msg = ip+' isn\'t registered, please confirm the IP Address and try again..'
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = "Please provide a valid IP Address."+correctFmt
            else:
              msg = "Please type in your WiFi Sensor IP Address."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_enable_message' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/NRF_enable_message | localID' \n\nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            if error == 0:
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,1,'sendAlert')
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
                msg = "Please provide a valid ID."+correctFmt
            else:
              msg = "Please type in your NRF Sensor localID."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_enable_message' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/IP_enable_message | ipaddress' \n\nWhere 'ipaddress' is the IP Address assigned to your WiFi Sensor."
            if error == 0:
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,1,'sendAlert')
                state = response[0]
                sensorName = response[1]
                if state == '1':
                  msg = 'Message update from '+sensorName+' ['+ip+'] has been enabled!!'
                elif state == 'A':
                  msg = 'Message update from '+sensorName+' ['+ip+'] is already enabled!!'
                elif state == '0':
                  msg = ip+' isn\'t registered, please confirm the IP Address and try again..'
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = "Please provide a valid IP Address."+correctFmt
            else:
              msg = "Please type in your WiFi Sensor IP Address."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_disable_sms' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/NRF_disable_sms | localID' \n\nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            if error == 0:
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,0,'sendSms')
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
                msg = "Please provide a valid ID."+correctFmt
            else:
              msg = "Please type in your NRF Sensor localID."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_disable_sms' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/IP_disable_sms | ipaddress' \n\nWhere 'ipaddress' is the IP Address assigned to your WiFi Sensor."
            if error == 0:
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,0,'sendSms')
                state = response[0]
                sensorName = response[1]
                if state == '1':
                  msg = 'SMS update from '+sensorName+' ['+ip+'] has been disabled!!'
                elif state == 'A':
                  msg = 'SMS update from '+sensorName+' ['+ip+'] is already disabled!!'
                elif state == '0':
                  msg = ip+' isn\'t registered, please confirm the IP Address and try again..'
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = "Please provide a valid IP Address."+correctFmt
            else:
              msg = "Please type in your WiFi Sensor IP Address."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_enable_sms' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/NRF_enable_sms | localID' \n\nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            if error == 0:
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,1,'sendSms')
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
                msg = "Please provide a valid ID."+correctFmt
            else:
              msg = "Please type in your NRF Sensor localID."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_enable_sms' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/IP_enable_sms | ipaddress' \n\nWhere 'ipaddress' is the IP Address assigned to your WiFi Sensor."
            if error == 0:
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,1,'sendSms')
                state = response[0]
                sensorName = response[1]
                if state == '1':
                  msg = 'SMS update from '+sensorName+' ['+ip+'] has been enabled!!'
                elif state == 'A':
                  msg = 'SMS update from '+sensorName+' ['+ip+'] is already enabled!!'
                elif state == '0':
                  msg = ip+' isn\'t registered, please confirm the IP Address and try again..'
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = "Please provide a valid IP Address."+correctFmt
            else:
              msg = "Please type in your WiFi Sensor IP Address."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_disable_media' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/NRF_disable_media | localID' \n\nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            if error == 0:
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,0,'useCam')
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
                msg = "Please provide a valid ID."+correctFmt
            else:
              msg = "Please type in your NRF Sensor localID."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_disable_media' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is: \n\n'/IP_disable_media | ipaddress' \n\nWhere 'ipaddress' is the IP Address assigned to your WiFi Sensor."
            if error == 0:
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,0,'useCam')
                state = response[0]
                sensorName = response[1]
                if state == '1':
                  msg = 'Media update from '+sensorName+' ['+ip+'] has been disabled!!'
                elif state == 'A':
                  msg = 'Media update from '+sensorName+' ['+ip+'] is already disabled!!'
                elif state == '0':
                  msg = ip+' isn\'t registered, please confirm the ID and try again..'
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = "Please provide a valid IP Address."+correctFmt
            else:
              msg = "Please type in your WiFi Sensor IP Address."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_enable_media' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/NRF_enable_media | localID' \n\nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            if error == 0:
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,1,'useCam')
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
                msg = "Please provide a valid ID."+correctFmt
            else:
              msg = "Please type in your NRF Sensor localID."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_enable_media' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = "The correct format is \n\n'/IP_enable_media | ipaddress' \n\nWhere 'ipaddress' is the IP Address assigned to your WiFi Sensor."
            if error == 0:
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,1,'useCam')
                state = response[0]
                sensorName = response[1]
                if state == '1':
                  msg = 'Media update from '+sensorName+' ['+ip+'] has been enabled!!'
                elif state == 'A':
                  msg = 'Media update from '+sensorName+' ['+ip+'] is already enabled!!'
                elif state == '0':
                  msg = ip+' isn\'t registered, please confirm the ID and try again..'
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = "Please provide a valid IP Address."+correctFmt
            else:
              msg = "Please type in your WiFi Sensor IP Address."+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_use_media' in commandL:
            try:
              media = commandS[1]
              localID = commandS[2]
            except Exception as e:
              media = '0'
            correctFmt = 'The correct format is: \n\n\'/NRF_use_media | video | localID\' or \n/NRF_use_media | image | localID \n\nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            if media.lower() == 'video':
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,'v','iOrv')
                state = response[0]
                sensorName = response[1]
                vidLength = response[2]
                camType = response[3]
                if camType == None:
                  state = 'C'
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
                  msg = 'The ID did not match any registered sensors. Please confirm the ID and try again, you entered: \''+localID+'\' as your NRF Sensor localID.'
                elif state == 'C':
                  msg = "Please configure the camera type to use first. Use the following command: \n\n'/NRF_use_camera | cameratype | SensorID | ipaddress'."
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = 'Please provide a valid ID.'+correctFmt
            elif media.lower() == 'image':
              if validate_localID(localID):
                response = updateNRFRegister(1,localID,'i','iOrv')
                state = response[0]
                sensorName = response[1]
                camType = response[3]
                if camType == None:
                  state = 'C'
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
                  msg = 'The ID did not match any registered sensors. Please confirm the ID and try again, you entered: \''+localID+'\' as your NRF Sensor localID.'
                elif state == 'C':
                  msg = "Please configure the camera type to use first. Use the following command: \n\n/NRF_use_camera | cameratype | SensorID | ipaddress"
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = 'Please provide a valid ID.'+correctFmt
            else:
              msg = 'Please specify either image or video and NRF sensor ID in your syntax.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_use_media' in commandL:
            try:
              media = commandS[1]
              ip = commandS[2]
            except Exception as e:
              media = '0'
            correctFmt = 'The correct format is: \n\n\'/IP_use_media | video | ipaddress\' or \n\'/IP_use_media | image | ipaddress\' \n\nWhere \'ipaddress\' is the IP Address assigned to your WiFi Sensor.'
            if media.lower() == 'video':
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,'v','iOrv')
                state = response[0]
                sensorName = response[1]
                vidLength = response[2]
                camType = response[3]
                if camType == None:
                  state = 'C'
                camIP = response[4]
                if state == '1':
                  if camType == 'ipcam':
                    msg = sensorName+' ['+ip+'] will send '+str(vidLength)+' Sec videos from '+camType+' '+camIP+' on sensor trigger!!'
                  else:
                    msg = sensorName+' ['+ip+'] will send '+str(vidLength)+' Sec videos from '+camType+' on sensor trigger!!'
                elif state == 'A':
                  if camType == 'ipcam':
                    msg = sensorName+' ['+ip+'] is already configured to send videos from '+camType+' '+camIP+' on sensor trigger!!'
                  else:
                    msg = sensorName+' ['+ip+'] is already configured to send videos from '+camType+' on sensor trigger!!'
                elif state == '0':
                  msg = 'The IP did not match any registered WiFi Sensors. Please confirm the IP and try again, you entered: \''+ip+'\' as your WiFi Sensor IP Address.'
                elif state == 'C':
                  msg = "Please configure the camera type to use first. Use the following command: \n\n'/IP_use_camera | cameratype | sensorIP | cameraIP'."
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = 'Please provide a valid IP Address.'+correctFmt
            elif media.lower() == 'image':
              if validate_ip(ip):
                response = updateWifiRegister(1,ip,'i','iOrv')
                state = response[0]
                sensorName = response[1]
                camType = response[3]
                if camType == None:
                  state = 'C'
                camIP = response[4]
                if state == '1':
                  if camType == 'ipcam':
                    msg = sensorName+' ['+ip+'] will send images from '+camType+' '+camIP+' on sensor trigger!!'
                  else:
                    msg = sensorName+' ['+ip+'] will send images from '+camType+' on sensor trigger!!'
                elif state == 'A':
                  if camType == 'ipcam':
                    msg = sensorName+' ['+ip+'] is already configured to send images from '+camType+' '+camIP+' on sensor trigger!!'
                  else:
                    msg = sensorName+' ['+ip+'] is already configured to send images from '+camType+' on sensor trigger!!'
                elif state == '0':
                  msg = 'The IP did not match any registered WiFi Sensors. Please confirm the IP and try again, you entered: \''+ip+'\' as your WiFi Sensor IP Address.'
                elif state == 'C':
                  msg = "Please configure the camera type to use first. Use the following command: \n\n/'IP_use_camera | cameratype | sensorIP | cameraIP'."
                else:
                  msg = 'Operation failed, please try again..'
              else:
                msg = 'Please provide a valid IP Address.'+correctFmt
            else:
              msg = 'Please specify either image or video and WiFi Sensor IP Address in your syntax.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass

        elif '/nrf_set_videolength' in commandL:
            try:
              length = commandS[1]
              localID = commandS[2]
              error = 0
            except Exception as e:
              error = 1
            correctFmt = "The correct format is: \n\n'/NRF_set_videolength | seconds | localID' \n\nWhere 'localID' is the first part of your sensor address e.g VIB001-234567 will have localID 'VIB001'."
            if error == 0:
              minTime = 3
              maxTime = 60
              lengthValid = validate_vid_length(length,minTime, maxTime)
              if lengthValid == True:
                if validate_localID(localID):
                  response = updateNRFRegister(1,localID,str(length),'vidLength')
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
                    msg = 'That ID is not registered.Please confirm the ID and try again, you entered: \''+localID+'\' as your NRF Sensor localID'
                  else:
                    msg = 'Operation failed, please try again..'
                else:
                  msg = "Please provide a valid ID. "+correctFmt
              else:
                msg = 'Please enter a valid number between '+str(minTime)+' and '+str(maxTime)+' as the video length. '+correctFmt
            else:
              msg = 'Use the correct syntax and try again. '+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_set_videolength' in commandL:
            try:
              length = commandS[1]
              ip = commandS[2]
              error = 0
            except Exception as e:
              error = 1
            correctFmt = "The correct format is: \n\n'/IP_set_videolength | seconds | ipaddress' \n\nWhere 'ipaddress' is the IP Address assigned to your WiFi Sensor."
            if error == 0:
              minTime = 3
              maxTime = 60
              lengthValid = validate_vid_length(length,minTime, maxTime)
              if lengthValid == True:
                if validate_ip(ip):
                  response = updateWifiRegister(1,ip,str(length),'vidLength')
                  state = response[0]
                  sensorName = response[1]
                  vidLength = response[2]
                  camType = response[3]
                  camIP = response[4]
                  if state == '1':
                    if camType.lower() == 'ipcam':
                      msg = sensorName+' ['+ip+'] will send '+str(length)+' Sec videos from '+camType+' '+camIP+' on sensor trigger when video mode is selected!!'
                    else:
                      msg = sensorName+' ['+ip+'] will send '+str(length)+' Sec videos from '+camType+' on sensor trigger when video mode is selected!!'
                  elif state == 'A':
                    if camType.lower() == 'ipcam':
                      msg = sensorName+' ['+ip+'] is already configured to send '+str(length)+' Sec videos from '+camType+' '+camIP+' on sensor trigger if video mode is selected!!'
                    else:
                      msg = sensorName+' ['+ip+'] is already configured to send '+str(length)+' Sec videos from '+camType+' on sensor trigger if video mode is selected!!'
                  elif state == '0':
                    msg = 'That IP is not registered.Please confirm the IP Address and try again, you entered: '+ip+' as your WiFi Sensor IP Address'
                  else:
                    msg = 'Operation failed, please try again..'
                else:
                  msg = "Please provide a valid IP Address. "+correctFmt
              else:
                msg = 'Please enter a valid number between '+str(minTime)+' and '+str(maxTime)+' as the video length. '+correctFmt
            else:
              msg = 'Use the correct syntax and try again. '+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_use_camera' in commandL:
            try:
              cam = commandS[1]
              localID = commandS[2]
              error = 0
            except Exception as e:
              print e
              error = 1
            correctFmt = 'The correct format is: \n\n\'/NRF_use_camera | cameratype | localID | ipaddress\' \n\nWhere cameratype is either: usbcam, picam or ipcam.\nIf camera type is ipcam you have to type its ip address in the ipaddress section.\n\'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            if error == 0:
              if validate_localID(localID):
                if cam == 'ipcam':
                  try:
                    ipAddr = commandS[3]
                    error = 0
                  except Exception as e:
                    print e
                    error = 1
                  if error == 0:
                    validIP = validate_ip(ipAddr)
                    if validIP == True:
                      response = updateNRFRegister(2,localID,cam,'camType',ipAddr,'camIP')
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
                    msg = 'Please provide an IP address. '+correctFmt
                elif cam == 'usbcam' or cam == 'picam':
                  response = updateNRFRegister(1,localID,cam,'camType')
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
                  msg = 'Please enter a valid camera type. '+correctFmt
              else:
                msg = "Please provide a valid ID. "+correctFmt
            else:
              msg = 'Please use the correct syntax and try again. '+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_use_camera' in commandL:
            try:
              cam = commandS[1]
              ip = commandS[2]
              error = 0
            except Exception as e:
              print e
              error = 1
            correctFmt = 'The correct format is: \n\n\'/IP_use_camera | cameratype | sensorIP | cameraIP\' \n\nWhere cameratype is either: usbcam, picam or ipcam.\nIf camera type is ipcam you have to type its ip address in the cameraIP section.\n\'sensorIP\' is the IP Address assigned to your WiFi Sensor.'
            if error == 0:
              if validate_ip(ip):
                if cam == 'ipcam':
                  try:
                    ipAddr = commandS[3]
                    error = 0
                  except Exception as e:
                    print e
                    error = 1
                  if error == 0:
                    validIP = validate_ip(ipAddr)
                    if validIP == True:
                      response = updateWifiRegister(2,ip,cam,'camType',ipAddr,'camIP')
                      state = response[0]
                      sensorName = response[1]
                      if state == '1':
                        msg = sensorName+' ['+ip+'] will use '+cam+' '+ipAddr+' for videos and images'
                      elif state == 'A':
                        msg = sensorName+' ['+ip+'] is already configured to use '+cam+' '+ipAddr+' for videos and images'
                      elif state == '0':
                        msg = ip+' isn\'t registered, please confirm the sensorIP and try again..'
                      else:
                        msg = 'Operation failed, please try again..'
                    else:
                      msg = 'You have entered an invalid cameraIP Address '+str(ipAddr)+', check the IP Address and try again. '+correctFmt
                  else:
                    msg = 'Please provide the cameraIP address. '+correctFmt
                elif cam == 'usbcam' or cam == 'picam':
                  response = updateWifiRegister(1,ip,cam,'camType')
                  state = response[0]
                  sensorName = response[1]
                  if state == '1':
                    msg = sensorName+' ['+ip+'] will use '+cam+' for videos and images'
                  elif state == 'A':
                    msg = sensorName+' ['+ip+'] is already configured to use '+cam+' for videos and images'
                  elif state == '0':
                    msg = ip+' isn\'t registered, please confirm the sensorIP and try again..'
                  else:
                    msg = 'Operation failed, please try again..'
                else:
                  msg = 'Please enter a valid camera type. '+correctFmt
              else:
                msg = "Please provide a valid IP Address for sensorIP. "+correctFmt
            else:
              msg = 'Please use the correct syntax and try again. '+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/capture' in commandL:
            msg = 'Done!'
            try:
              media = commandS[1]
              camType = commandS[2]
              error = 0
            except Exception as e:
              error = 1
              print e
            correctFmt = 'The correct format is: \n\n\'/Capture | media | cameratype | seconds | ipaddress\' \n\nWhere media is either video or image, cameratype either picam, usbcam or ipcam and seconds the number of seconds if video is selected. If ipcam is selected you have to provide an IP Address in the last section \'ipaddress\'.'
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
                        msg = 'Please provide an IP Address. '+correctFmt
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
                      msg = 'Please select the right camera type. '+correctFmt
                  else:
                    msg = 'Please enter a valid number between '+str(minTime)+' and '+str(maxTime)+' as the video length. '+correctFmt
                else:
                  msg = 'Please specify a camera type and the number of seconds you want for video. '+correctFmt
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
                    msg = 'Please provide an IP Address. '+correctFmt
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
                  msg = 'Please select the right camera type. '+correctFmt
                pass
              else:
                msg = 'You have entered an invalid media type, please type video or image as media type. '+correctFmt
            else:
              msg = 'Please provide media type you want to capture and camera type. '+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_register_sensor' in commandL:
            try:
              nodeID = commandS[1]
              localID = commandS[2]
              uniqueID = commandS[3]
              description = commandS2[4]
              error = 0
            except Exception as e:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/NRF_register_sensor | nodeID | localID | globalID | description\' \n\nWhere \'nodeID\' is the number in localID address e.g sensor address VIB001-234567 will have nodeID 1. \'localID\' is the first part of sensor address e.g VIB001. \'globalID\' is the second part of your sensor address e.g 234567. \'description \' is the name or description you give to identify your sensor e.g Front door vibration sensor'
            if error == 0:
              if validate_nodeID(nodeID):
                 if validate_localID(localID):
                   if validate_uniqueID(uniqueID):
                     if validate_description(description):
                       if int(localID[3:6]) == int(nodeID):
                         regTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                         mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                         cursor1 = mariadb_connection.cursor()
                         try:
                           cursor1.execute("INSERT INTO registeredNRFSensors (nodeID,sensorName,localID,globalID,regDate) VALUES(%s,'%s','%s',%s,'%s')"%(str(nodeID),str(description),str(localID),str(uniqueID),str(regTime)))
                           rowCount = cursor1.rowcount
                           cursor1.close()
                           mariadb_connection.commit()
                           if rowCount >= 1:
                             msg = description+'['+localID+'] has been registered!!'
                           else:
                             msg = description+'['+localID+'] has not been registered!! confirm your entries and try again.'
                         except mariadb.Error as error:
                           print("Error: {}".format(error))
                           msg = 'Error occurred. Make sure there is no other sensor registered with the same nodeID and try again..'
                         mariadb_connection.close()
                       else:
                         msg = 'nodeID should be the same number as the digit part of localID. e.g. if sensor address is VIB255-234567, localID is VIB255, nodeID should be typed as 255.'
                     else:
                       msg = 'Please provide a short description or name to identify your sensor.'+correctFmt
                   else:
                     msg = 'Please type the correct globalID. If your sensor address is VIB001-234567 the globalID is 234567.'+correctFmt
                 else:
                   msg = 'Please type the correct localID. If your sensor address is VIB001-234567 the localID is VIB001.'+correctFmt
              else:
                msg = 'Please type the correct nodeID, it should be a number between 1 and 255.'+correctFmt
            else:
              msg = 'Sensor registration failed. Please use the correct format and fill in every section.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_register_sensor' in commandL:
            try:
              ip = commandS[1]
              description = commandS2[2]
              error = 0
            except Exception as e:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/IP_register_sensor | ipaddress | description\' \n\nWhere \'ipaddress\' is the IP Address of your sensor. \'description \' is the name or description you give to identify your sensor e.g Lounge area motion sensor'
            if error == 0:
              if validate_ip(ip):
                if validate_description(description):
                  regTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                  cursor1 = mariadb_connection.cursor()
                  try:
                    cursor1.execute("INSERT INTO registeredWifiSensors (IP,sensorName,regDate) VALUES('%s','%s','%s')"%(str(ip),str(description),str(regTime)))
                    rowCount = cursor1.rowcount
                    cursor1.close()
                    mariadb_connection.commit()
                    if rowCount >= 1:
                      msg = description+'['+ip+'] has been registered!!'
                    else:
                      msg = description+'['+ip+'] has not been registered!! confirm your entries and try again.'
                  except mariadb.Error as error:
                    print("Error: {}".format(error))
                    msg = 'Error occurred. Make sure there is no other sensor registered with the same IP Address and try again..'
                  mariadb_connection.close()
                else:
                  msg = 'Please provide a short description or name to identify your sensor.'+correctFmt
              else:
                msg = 'Please provide a valid IP Address.'+correctFmt
            else:
              msg = 'Sensor registration failed. Please use the correct format and fill in every section.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ipcam_register_camera' in commandL:
            try:
              ip = commandS[1]
              description = commandS2[2]
              error = 0
            except Exception as e:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/IPCam_register_camera | ipaddress | description\' \n\nWhere \'ipaddress\' is the IP Address of your camera. \'description \' is the name or description you give to identify your camera e.g Lounge area IP camera'
            if error == 0:
              if validate_ip(ip):
                if validate_description(description):
                  regTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                  cursor1 = mariadb_connection.cursor()
                  try:
                    cursor1.execute("INSERT INTO registeredIPCameras (IP,camName,regDate) VALUES('%s','%s','%s')"%(str(ip),str(description),str(regTime)))
                    rowCount = cursor1.rowcount
                    cursor1.close()
                    mariadb_connection.commit()
                    if rowCount >= 1:
                      msg = description+'['+ip+'] has been registered!!'
                    else:
                      msg = description+'['+ip+'] has not been registered!! confirm your entries and try again.'
                  except mariadb.Error as error:
                    print("Error: {}".format(error))
                    msg = 'Error occurred. Make sure there is no other camera registered with the same IP Address and try again..'
                  mariadb_connection.close()
                else:
                  msg = 'Please provide a short description or name to identify your camera.'+correctFmt
              else:
                msg = 'Please provide a valid IP Address.'+correctFmt
            else:
              msg = 'Camera registration failed. Please use the correct format and fill in every section.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_remove_sensor' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/NRF_remove_sensor | localID\' \n\nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            if error == 0:
              if validate_localID(localID):
                mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                cursor1 = mariadb_connection.cursor()
                try:
                  cursor1.execute("SELECT * FROM registeredNRFSensors WHERE localID = '%s'"%(localID))
                  result = cursor1.fetchall()
                  rowCount = len(result)
                  cursor1.close()
                  if rowCount >= 1:
                    for row in result:
                      sensorName = row[1]
                      cursor2 = mariadb_connection.cursor()
                      try:
                        cursor2.execute("DELETE FROM registeredNRFSensors WHERE localID = '%s'"%(localID))
                        rowCount = cursor2.rowcount
                        cursor2.close()
                        mariadb_connection.commit()
                        if rowCount >= 1:
                          msg = sensorName+'['+localID+'] has been deleted'
                        else:
                          msg = 'Operation failed, please try again.'+correctFmt
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
                msg = 'Please type in a valid ID.'+correctFmt
            else:
              msg =  'Please provide the localID of the sensor you want to remove.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_remove_sensor' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/IP_remove_sensor | ipaddress\' \n\nWhere \'ipaddress\' is the IP Address of your sensor.'
            if error == 0:
              if validate_ip(ip):
                mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                cursor1 = mariadb_connection.cursor()
                try:
                  cursor1.execute("SELECT * FROM registeredWifiSensors WHERE IP = '%s'"%(str(ip)))
                  result = cursor1.fetchall()
                  rowCount = len(result)
                  cursor1.close()
                  if rowCount >= 1:
                    for row in result:
                      sensorName = row[1]
                      cursor2 = mariadb_connection.cursor()
                      try:
                        cursor2.execute("DELETE FROM registeredWifiSensors WHERE IP = '%s'"%(str(ip)))
                        rowCount = cursor2.rowcount
                        cursor2.close()
                        mariadb_connection.commit()
                        if rowCount >= 1:
                          msg = sensorName+'['+ip+'] has been deleted'
                        else:
                          msg = 'Operation failed, please try again.'+correctFmt
                      except mariadb.Error as error:
                        print("Error: {}".format(error))
                        msg = 'Database error occurred. Please retry later.'
                  else:
                    msg = 'The IP \''+ip+'\' did not match any registered WiFi sensors. Please confirm your IP Address and try again..'
                except mariadb.Error as error:
                  print("Error: {}".format(error))
                  msg = 'Database error occurred. Please retry later.'
                mariadb_connection.close()
              else:
                msg = 'Please type in a valid IP.'+correctFmt
            else:
              msg =  'Please provide the IP Address of the WiFi sensor you want to remove.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ipcam_remove_camera' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/IPCam_remove_camera | ipaddress\' \n\nWhere \'ipaddress\' is the IP Address of your camera.'
            if error == 0:
              if validate_ip(ip):
                mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                cursor1 = mariadb_connection.cursor()
                try:
                  cursor1.execute("SELECT * FROM registeredIPCameras WHERE IP = '%s'"%(str(ip)))
                  result = cursor1.fetchall()
                  rowCount = len(result)
                  cursor1.close()
                  if rowCount >= 1:
                    for row in result:
                      sensorName = row[1]
                      cursor2 = mariadb_connection.cursor()
                      try:
                        cursor2.execute("DELETE FROM registeredIPCameras WHERE IP = '%s'"%(str(ip)))
                        rowCount = cursor2.rowcount
                        cursor2.close()
                        mariadb_connection.commit()
                        if rowCount >= 1:
                          msg = sensorName+'['+ip+'] has been deleted'
                        else:
                          msg = 'Operation failed, please try again.'+correctFmt
                      except mariadb.Error as error:
                        print("Error: {}".format(error))
                        msg = 'Database error occurred. Please retry later.'
                  else:
                    msg = 'The IP \''+ip+'\' did not match any registered cameras. Please confirm your IP Address and try again..'
                except mariadb.Error as error:
                  print("Error: {}".format(error))
                  msg = 'Database error occurred. Please retry later.'
                mariadb_connection.close()
              else:
                msg = 'Please type in a valid IP.'+correctFmt
            else:
              msg =  'Please provide an IP Address of the camera you want to remove.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_show_configuration' in commandL:
            try:
              localID = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/NRF_show_configuration | localID\' \n\nWhere \'localID\' is the first part of your sensor address e.g VIB001-234567 will have localID \'VIB001\'.'
            if error == 0:
              if validate_localID(localID):
                mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                cursor1 = mariadb_connection.cursor()
                try:
                  cursor1.execute("SELECT * FROM registeredNRFSensors WHERE localID = '%s'"%(localID))
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
                      batt = row[14]
                      def checkActive(active):
                        if active != None:
                          if active == 1:
                            return 'Active'
                          else:
                            return 'Offline'
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
                      def checkBatt(batt):
                        if batt != None:
                          return str(batt)+'%'
                        else:
                          return 'Unknown'
                      msg = sensorName+"["+localID+"] \nconfiguration: \n\nStatus: "+checkActive(active)+" \n\nLast Seen :"+checkLastSeen(lastSeen)+" \n\nSend alert on trigger: "+returnYesOrNo(sendAlert)+" \n\nSend SMS alerts: "+returnYesOrNo(sendSms)+" \n\nSend media on trigger: "+returnYesOrNo(useCam)+" \n\nUse camera type: "+checkCamTypeOrIP(camType)+"\n\nIP Camera address: "+checkCamTypeOrIP(camIP)+" \n\nUse media: "+checkMedia(media)+" \n\nVideo length for video mode: "+str(vidLength)+"\n\nBattery Level: "+checkBatt(batt)
                  else:
                    msg = 'There is no sensor registered as \''+localID+'\'.'
                except mariadb.Error as error:
                  print("Error: {}".format(error))
                  msg = 'Database error occurred. Please retry later.'
                mariadb_connection.close()
              else:
                msg = 'Please type a valid ID.'+correctFmt
            else:
              msg = 'Please provide a valid ID to check NRF sensor configuration.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_show_configuration' in commandL:
            try:
              ip = commandS[1]
              error = 0
            except:
              error = 1
            correctFmt = 'The correct format is: \n\n\'/IP_show_configuration | ipaddress\' \n\nWhere \'ipaddress\' is the IP Address of your WiFi sensor.'
            if error == 0:
              if validate_ip(ip):
                mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
                cursor1 = mariadb_connection.cursor()
                try:
                  cursor1.execute("SELECT * FROM registeredWifiSensors WHERE IP = '%s'"%(ip))
                  result = cursor1.fetchall()
                  rowCount = len(result)
                  cursor1.close()
                  if rowCount >= 1:
                    for row in result:
                      sensorName = row[1]
                      active = row[2]
                      lastSeen = row[3]
                      camType = row[5]
                      camIP = row[6]
                      media = row[7]
                      vidLength = row[8]
                      sendAlert = row[9]
                      sendSms = row[10]
                      useCam = row[11]
                      batt = row[12]
                      def checkActive(active):
                        if active != None:
                          if active == 1:
                            return 'Active'
                          else:
                            return 'Offline'
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
                      def checkBatt(batt):
                        if batt != None:
                          return str(batt)+'%'
                        else:
                          return 'Unknown'
                      msg = sensorName+"["+ip+"] \nconfiguration: \n\nStatus: "+checkActive(active)+" \n\nLast Seen :"+checkLastSeen(lastSeen)+" \n\nSend alert on trigger: "+returnYesOrNo(sendAlert)+" \n\nSend SMS alerts: "+returnYesOrNo(sendSms)+" \n\nSend media on trigger: "+returnYesOrNo(useCam)+" \n\nUse camera type: "+checkCamTypeOrIP(camType)+"\n\nIP Camera address: "+checkCamTypeOrIP(camIP)+" \n\nUse media: "+checkMedia(media)+" \n\nVideo length for video mode: "+str(vidLength)+"\n\nBattery Level: "+checkBatt(batt)
                  else:
                    msg = 'There is no WiFi sensor with IP Address \''+ip+'\'.'
                except mariadb.Error as error:
                  print("Error: {}".format(error))
                  msg = 'Database error occurred. Please retry later.'
                mariadb_connection.close()
              else:
                msg = 'Please type a valid IP Address.'+correctFmt
            else:
              msg = 'Please provide a valid IP Address to check WiFi sensor configuration.'+correctFmt
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/nrf_show_registered_sensors' in commandL:
            mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
            cursor1 = mariadb_connection.cursor()
            try:
              cursor1.execute("SELECT * FROM registeredNRFSensors")
              result = cursor1.fetchall()
              rowCount = len(result)
              cursor1.close()
              if rowCount >= 1:
                msg = 'Registered NRF Sensors:'
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
                      msg += '\n\n'+str(count)+'. ['+localID+'][Offline] '+sensorName+'. Last seen: '+str(lastSeen)
                    else:
                      msg += '\n\n'+str(count)+'. ['+localID+'][Offline] '+sensorName+'.'
              else:
                msg = 'You have no registered NRF sensors!!'
            except mariadb.Error as error:
              print("Error: {}".format(error))
              msg = 'Database error occurred. Please retry later.'
            mariadb_connection.close()
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/ip_show_registered_sensors' in commandL:
            mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
            cursor1 = mariadb_connection.cursor()
            try:
              cursor1.execute("SELECT * FROM registeredWifiSensors")
              result = cursor1.fetchall()
              rowCount = len(result)
              cursor1.close()
              if rowCount >= 1:
                msg = 'Registered WiFi Sensors:'
                count = 0
                for row in result:
                  count += 1
                  ip = row[0]
                  sensorName = row[1]
                  active = row[2]
                  lastSeen = row[3]
                  if active == 1:
                    if lastSeen != None:
                      msg += '\n\n'+str(count)+'. ['+ip+'][Active] '+sensorName+'. Last seen: '+str(lastSeen)
                    else:
                      msg += '\n\n'+str(count)+'. ['+ip+'][Active] '+sensorName+'.'
                  else:
                    if lastSeen != None:
                      msg += '\n\n'+str(count)+'. ['+ip+'][Offline] '+sensorName+'. Last seen: '+str(lastSeen)
                    else:
                      msg += '\n\n'+str(count)+'. ['+ip+'][Offline] '+sensorName+'.'
              else:
                msg = 'You have no registered wifi sensors!!'
            except mariadb.Error as error:
              print("Error: {}".format(error))
              msg = 'Database error occurred. Please retry later.'
            mariadb_connection.close()
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/show_available_camera' in commandL:
            output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Images/usb1camimg.jpg"])
            output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takeUSB1CamImg.sh", "/home/pi/Watchman/Images/usb1camimg.jpg"])
            fileExists = os.path.exists('/home/pi/Watchman/Images/usb1camimg.jpg')
            if fileExists == True:
              usbcam = 'available'
            else:
              usbcam = 'offline'
            output = subprocess.call(["sudo", "rm", "/home/pi/Watchman/Images/picamimg.jpg"])
            output = subprocess.call(["sudo", "/home/pi/Watchman/Images/takePiCamImg.sh", "/home/pi/Watchman/Images/picamimg.jpg"])
            fileExists = os.path.exists('/home/pi/Watchman/Images/picamimg.jpg')
            if fileExists == True:
              picam = 'available'
            else:
              picam = 'offline'
            mariadb_connection = mariadb.connect(user=usr, password=pswd, database=db)
            cursor1 = mariadb_connection.cursor()
            try:
              cursor1.execute("SELECT * FROM registeredIPCameras")
              result = cursor1.fetchall()
              rowCount = len(result)
              cursor1.close()
              msg = 'Cameras:\n'
              msg += "1. Raspberry Pi Camera [picam]["+picam+"]\n\n"
              msg += "2. USB Camera [usbcam]["+usbcam+"]"
              if rowCount >= 1:
                count = 2
                for row in result:
                  count += 1
                  ip = row[0]
                  sensorName = row[1]
                  active = row[2]
                  lastSeen = row[3]
                  if active == 1:
                    if lastSeen != None:
                      msg += '\n\n'+str(count)+'. IP Camera[ipcam]['+ip+'][Active] '+sensorName+'. Last seen: '+str(lastSeen)
                    else:
                      msg += '\n\n'+str(count)+'. IP Camera[ipcam]['+ip+'][Active] '+sensorName+'.'
                  else:
                    if lastSeen != None:
                      msg += '\n\n'+str(count)+'. IP Camera[ipcam]['+ip+'][Offline] '+sensorName+'. Last seen: '+str(lastSeen)
                    else:
                      msg += '\n\n'+str(count)+'. IP Camera[ipcam]['+ip+'][Offline] '+sensorName+'.'
              else:
                msg += '\n\nYou have no registered IP cameras'
            except mariadb.Error as error:
              print("Error: {}".format(error))
              msg = 'Database error occurred. Please retry later.'
            mariadb_connection.close()
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif commandL == '/disable_gprs':
            try:
              c = open("/home/pi/Watchman/useGprs.txt","r")
              status = c.read()
              status = status.strip()
              c.close()
              if status == '1':
                msg = 'Stopping GPRS..'
                subprocess.Popen(['sudo','/home/pi/Watchman/closeGprs.py'])
              else:
                msg = 'GPRS is not active.'
            except:
              msg = 'Error Stopping GPRS..'
            telegram_bot.sendMessage(chat_id, str(msg))
            subprocess.Popen(['sudo','/home/pi/Watchman/closeGprs.py'])
        elif commandL == '/stop':
            response = updateNRFRegister(0,'*',0,'sendAlert')
            response2 = updateWifiRegister(0,'*',0,'sendAlert')
            state = response[0]
            state2 = response2[0]
            msg = 'Hi, '
            if (state == '1')or(state2 == '1'):
              msg += 'message update from all sensors have been disabled, you will no longer receive any updates. \nType /Start to enable updates from sensors.'
            if (state == 'A') or (state2 == 'A'):
              msg += 'message update from all sensors have already been disabled, you will no longer receive any updates. \nType /Start to enable updates from sensors.'
            if state == '0':
              msg += '\nThere was an error stopping NRF sensors, have you registered any NRF sensors? ..'
            if state2 == '0':
              msg += '\nThere was an error stoppng WiFi sensors, have you registered any WiFi sensors? ..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif commandL == '/start':
            response = updateNRFRegister(0,'*',1,'sendAlert')
            response2 = updateWifiRegister(0,'*',1,'sendAlert')
            state = response[0]
            state2 = response2[0]
            msg = 'Hi, '
            if (state == '1')or(state2 == '1'):
              msg += 'message update from all sensors have been enabled, you will receive updates from all sensors. \nType /Stop to disable updates from sensors.'
            if (state == 'A') or (state2 == 'A'):
              msg += 'message update from all sensors have already been enabled, you will receive updates from all sensors. \nType /Stop to disable updates from sensors.'
            if state == '0':
              msg += '\nThere was an error starting NRF sensors, have you registered any NRF sensors? ..'
            if state2 == '0':
              msg += '\nThere was an error starting WiFi sensors, have you registered any WiFi sensors? ..'
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif commandL == '/temperature':
            t=float(subprocess.check_output(["/opt/vc/bin/vcgencmd measure_temp  |  cut -c6-9"], shell=True)[:-1])
            ts=str(t)
            answer = 'Device temperature is '+ts+' °C'
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
    else:
        telegram_bot.sendMessage (chat_id, 'Hi, please set your username by sending the following SMS:\n\nSet_telegram_username|username\n\nwhere \'username\' is your firstname on Telegram')

c = open("/home/pi/Watchman/TelegramBot/isBotRunning.txt","r")
status = c.read()
status = status.strip()
c.close()
if status == '1':
    ts = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    print '['+ts + '] bot already running!!'
    exit()

token = token.strip()

telegram_bot = telepot.Bot(token)
print (telegram_bot.getMe())

try:
  MessageLoop(telegram_bot, action).run_as_thread()
except Exception as e:
  print '['+datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")+'] Error: {}'.format(e)
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

