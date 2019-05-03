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
mariadb_connection = mariadb.connect(user='watch', password='mawe',database='watchman')

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
            msg = ' '
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
                cursor2 = mariadb_connection.cursor()
                try:
                  cursor2.execute("UPDATE registeredSensors SET sendAlert = '%s' WHERE localID = '%s'"%('0',str(localID)))
                  rowCount = cursor2.rowcount
                  cursor2.close()
                  #print rowCount
                  if rowCount >= 1:
                    msg = 'Message update from '+sensorName+' ['+localID+'] has been disabled!!'
                  else:
                    msg = 'Message update from '+sensorName+' ['+localID+'] has already been disabled!!'
                except mariadb.Error as error:
                  print("Error: {}".format(error))
                mariadb_connection.commit()
              else:
                msg = localID+' isn\'t registered, please confirm the Id and try again..'
            except mariadb.Error as error:
              print("Error: {}".format(error))
            telegram_bot.sendMessage(chat_id, str(msg))
            pass
        elif '/enable_message_' in commandL:
            localID = commandS[2]
            msg = ' '
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
                cursor2 = mariadb_connection.cursor()
                try:
                  cursor2.execute("UPDATE registeredSensors SET sendAlert = '%s' WHERE localID = '%s'"%('1',str(localID)))
                  rowCount = cursor2.rowcount
                  cursor2.close()
                  #print rowCount
                  if rowCount >= 1:
                    msg = 'Message update from '+sensorName+' ['+localID+'] has been enabled!!'
                  else:
                    msg = 'Message update from '+sensorName+' ['+localID+'] has already been enabled!!'
                except mariadb.Error as error:
                  print("Error: {}".format(error))
                mariadb_connection.commit()
              else:
                msg = localID+' isn\'t registered, please confirm the Id and try again..'
            except mariadb.Error as error:
              print("Error: {}".format(error))
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
        elif '/use_pic_cam1' in commandL:
            o = open("/home/pi/Watchman/imageOrVideoCam1.txt","w+")
            o.write('i')
            o.close()
            telegram_bot.sendMessage (chat_id, str("I will send pictures on sensor triggers for Cam1.."))
        elif '/use_pic_cam2' in commandL:
            o = open("/home/pi/Watchman/imageOrVideoCam2.txt","w+")
            o.write('i')
            o.close()
            telegram_bot.sendMessage (chat_id, str("I will send pictures on sensor triggers for Cam2.."))
        elif '/use_pic' in commandL:
            o = open("/home/pi/Watchman/imageOrVideoCam1.txt","w+")
            o.write('i')
            o.close()
            o = open("/home/pi/Watchman/imageOrVideoCam2.txt","w+")
            o.write('i')
            o.close()
            telegram_bot.sendMessage (chat_id, str("I will send pictures on sensor triggers for all cameras.."))
        elif '/use_video_cam1' in commandL:
            o = open("/home/pi/Watchman/imageOrVideoCam1.txt","w+")
            o.write('v')
            o.close()
            telegram_bot.sendMessage (chat_id, str("I will send videos on sensor triggers for Cam1.."))
        elif '/use_video_cam2' in commandL:
            o = open("/home/pi/Watchman/imageOrVideoCam2.txt","w+")
            o.write('v')
            o.close()
            telegram_bot.sendMessage (chat_id, str("I will send videos on sensor triggers for Cam2.."))
        elif '/use_video' in commandL:
            o = open("/home/pi/Watchman/imageOrVideoCam1.txt","w+")
            o.write('v')
            o.close()
            o = open("/home/pi/Watchman/imageOrVideoCam2.txt","w+")
            o.write('v')
            o.close()
            telegram_bot.sendMessage (chat_id, str("I will send videos on sensor triggers for all cameras.."))
        elif '/disable_vibration_sensor' in commandL:
            v = open("/home/pi/Watchman/allowToSendVibMsg.txt","w+")
            v.write('0')
            v.close()
            telegram_bot.sendMessage (chat_id, str("Vibration sensor disabled!!"))
        elif '/enable_vibration_sensor' in commandL:
            v = open("/home/pi/Watchman/allowToSendVibMsg.txt","w+")
            v.write('1')
            v.close()
            telegram_bot.sendMessage (chat_id, str("Vibration sensor enabled!!"))
        elif '/disable_motion_sensor' in commandL:
            m = open("/home/pi/Watchman/allowToSendMotionMsg.txt","w+")
            m.write('0')
            m.close()
            telegram_bot.sendMessage (chat_id, str("Motion sensor disabled!!"))
        elif '/enable_motion_sensor' in commandL:
            m = open("/home/pi/Watchman/allowToSendMotionMsg.txt","w+")
            m.write('1')
            m.close()
            telegram_bot.sendMessage (chat_id, str("Motion sensor enabled!!"))
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
    mariadb_connection.close()

