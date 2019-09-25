#!/usr/bin/env python
import os,time,sys
import serial
import time
import subprocess
import socket
import telepot
from datetime import datetime
import paho.mqtt.client as mqtt
import mysql.connector as mariadb
import MySQLdb
from ConfigParser import SafeConfigParser


def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    topic = message.topic
    qos = message.qos
    retainFlag = message.retain
    print("message received " ,msg)
    print("message topic=",topic)
    print("message qos=",qos)
    print("message retain flag=",retainFlag)
    if topic == 'closeCheckSimEvents':
      global exit
      exit = True
    elif topic == 'sendSMS':
      send_msg(msg)
    elif topic == 'callNumber':
      global callingAdmin
      callingAdmin = True
      print 'Calling Number '+msg
      call_number(msg)

def convert_to_string(buf):
    try:
        tt =  buf.decode('utf-8').strip()
        return tt
    except UnicodeError:
        tmp = bytearray(buf)
        for i in range(len(tmp)):
            if tmp[i]>127:
                tmp[i] = ord('#')
        return bytes(tmp).decode('utf-8').strip()

        try:
            ser=serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2)
        except Exception as e:
            exitScript(e)

def setup():
  command('ATE0\n')         # command echo off
  command('AT+CLIP=1\n')    # caller line identification
  command('AT+CMGF=1\n')    # plain text SMS
  command('AT+CLTS=1\n')    # enable get local timestamp mode
  command('AT+CSCLK=0\n')   # disable automatic sleep

def command(cmdstr, lines=1, waitfor=500, msgtext=None):
    while ser.in_waiting:
        ser.readline()
    ser.write(cmdstr.encode())
    if msgtext:
        ser.write(msgtext.encode())
    if waitfor>1000:
        time.sleep((waitfor-1000)/1000)
    buf=ser.readline() #discard linefeed etc
    #print(buf)
    buf=ser.readline()
    if not buf:
        return None
    result = convert_to_string(buf)
    if lines>1:
        for i in range(lines-1):
            global savbuf
            buf=ser.readline()
            if not buf:
                return result
            buf = convert_to_string(buf)
            if not buf == '' and not buf == 'OK':
                savbuf += buf+'\n'
                #print('savbuf: {}'.format(savbuf))
    return result

def send_sms(destno,msgtext):
  global sendingSms
  if not sendingSms:
    sendingSms = True
    if alive(3):
      global _buffer
      _buffer = ''
      ser.write('AT+CMGS="{}"\n'.format(destno))
      time.sleep(2)
      ser.write(msgtext.encode()+'\x1A\r\n')
      count = 0
      buf = ''
      while len(_buffer) < 4 and len(buf) < 4:
        count += 1
        if count > 9:
          break
        buf = ser.readline()
        print str(count)+'. Waiting for response..'+str(len(_buffer))+' '+str(len(buf))
        time.sleep(1)
      if ('+CMGS' or '+CUSD' in _buffer) or ('+CMGS' or '+CUSD' in buf):
        sendingSms = False
        return 'OK'
      else:
        print 'SMS not sent!'
        sendingSms = False
        return 'error'
      #result = command('AT+CMGS="{}"\n'.format(destno),99,5000,msgtext+'\x1A')
    else:
      subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
      sendingSms = False
      return 'No Response'

def send_msg(msg):
    print 'Sending SMS..'
    if len(str(admin)) > 2:
      result = send_sms(admin,msg)
      if not 'OK' in result:
        print 'failed, calling admin..'
        global msgToAdmin
        msgToAdmin = "Sending text message failed. Airtime balance may be depleted. Try loading more airtime."
        if alive(6):
          if len(str(reverseCallAdmin)) > 2:
            call_number(reverseCallAdmin)
        else:
          print 'No GSM Module found!!'
          subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
      else:
        print 'SMS sent!'

def send_ussd(ussd):
  result = command('AT+CUSD=1,\"'+str(ussd)+'\",15\r')
  if 'OK' in result:
    return True
  else:
    return False

def read_sms(id):
    result = command('AT+CMGR={}\n'.format(id),99)
    if result:
        params=result.split(',')
        if not params[0] == '':
            params2 = params[0].split(':')
            if params2[0]=='+CMGR':
                number = params[1].replace('"',' ').strip()
                date   = params[3].replace('"',' ').strip()
                time   = params[4].replace('"',' ').strip()
                #return  [number,date,time,savbuf]
                return [number,savbuf]
    return None

def call_number(num):
    print 'Calling: '+num
    command('AT+MORING=1\r\n')
    command('ATD'+num+';\r\n')

def alive(n):
    for x in range(1,n+1):
      if x == 5:
        subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
        time.sleep(5)
      print str(x)+' checking sim800l..'
      result = command('AT\n')
      if result != None:
        if 'OK' in result:
          return True
    return False
def delete_sms(id):
    command('AT+CMGD={}\n'.format(id),1)

def delete_all_sms():
    command('AT+CMGDA="DEL ALL"\n',1)

def checkInternet(hostname):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80))
    s.close()
    return True
  except:
     pass
  return False

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

def validate_phoneNo(no):
    num = str(no)
    num = num.replace("+","")
    num = num.replace("#","")
    num = num.replace("*","")
    numlen = len(num)
    if numlen < 8:
        return False
    if not num.isdigit():
        return False
    return True

def validate_token(tn):
    tok = str(tn)
    toklen = len(tok)
    if toklen < 30:
        return False
    return True

#method to play audio messages to admin if we call the admin
def playMsgIfCallingUser():
  global msgToAdmin
  print 'Admin has been called, now playing pending message'
  if len(msgToAdmin) > 5:
    subprocess.call(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/msgToAdmin.wav',msgToAdmin])
    subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/msgToAdmin.wav'])
    msgToAdmin = ''
  else:
    c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","r")
    msg = c.read()
    immediateMsg = 'You have no new message, '
    if len(msg) > 2:
      immediateMsg = 'You have a message, '+msg+', '
    c.close()
    lastMsg = 'Thank you for your time and have a nice day.'
    subprocess.Popen(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/secondCallingMsg.wav',immediateMsg+lastMsg])
    subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/firstCallingMsg.wav'])
    subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/secondCallingMsg.wav'])
    #Clear text file once the message has been played to user
    c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","w")
    c.write('0')
    c.close()

#method to play audio message if admin calls us
def playMsgIfUserCalled():
  print 'Admin called us, now playing status and pending messages'
  #check if we have pending messages..
  c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","r")
  msg = c.read()
  pendingMsg = 'You have no pending messages, '
  if len(msg) > 2:
    pendingMsg = 'You have some pending messages. '+msg
  c.close()

  #check the battery status and if we are running on mains power or battery power
  b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","r")
  msg = b.read()
  battMsg = 'Power source and battery status is unknown, '
  if len(msg) > 4:
    splitMsg = msg.split('#')
    source = splitMsg[0]
    level = splitMsg[1]
    sourceMsg = 'The system is running on mains power. '
    if(source == '1'):
      sourceMsg = 'The system is running on battery power. '
    battMsg = sourceMsg+'The battery level is, '+level+'.  '
  b.close()

  #play first msg as we process other commands..
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/firstCalledMsg.wav'])

  #check if we are connected to the internet
  netMsg = 'Ping to google servers failed, there is no connection to the internet. You will not receive sensor messages via telegram, until internet connection is restored. '
  if(checkInternet(REMOTE_SERVER)):
    netMsg = 'Internet connection is available, I will be sending all sensor messages, to you via telegram. '

  lastMsg = 'Thank you for your time and have a nice day.'

  subprocess.call(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/secondCalledMsg.wav',pendingMsg+battMsg+netMsg+lastMsg])
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/secondCalledMsg.wav'])

  #Clear text file once the message has been played to user
  c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","w")
  c.write('0')
  c.close()

def executeSmsCmd(sms):
  splitSms = sms.split('|')
  if 'ussd|' in sms.lower():
    ussd = splitSms[1]
    ussd = ussd.strip()
    send_ussd(ussd)
    pass
  elif 'show_config_commands' in sms.lower():
    send_msg('Config Commands:\n1.Connect_wifi\n2.Set_admin_number\n3.Set_callback_number\n4.Set_telegram_username\n5.Set_telegram_token\n6.Set_static_IP\n7.Configure_sensor')
    pass
  elif 'set_admin_n' in sms.lower():
    correctFmt = 'The correct format is:\n\nSet_admin_number|phoneNo'
    adminNo = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      adminNo = splitsms[1].strip()
    except:
      error = 1
    if error == 0:
      if validate_phoneNo(adminNo):
        subprocess.call(['sudo','/home/pi/Watchman/saveWatchmanConfig.py','admin_no',str(adminNo)])
        msg='Admin Number has been updated.'
      else:
        msg='Please type a valid phone number.\n'+correctFmt
    else:
      msg = correctFmt
    send_msg(msg)
    pass
  elif 'set_callback_n' in sms.lower():
    correctFmt = 'The correct format is:\n\nSet_callback_number|phoneNo'
    callbackNo = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      callbackNo = splitsms[1].strip()
    except:
      error = 1
    if error == 0:
      if validate_phoneNo(callbackNo):
        subprocess.call(['sudo','/home/pi/Watchman/saveWatchmanConfig.py','callback_no',str(callbackNo)])
        msg='Callback Number has been updated.'
      else:
        msg='Please type a valid phone number.\n'+correctFmt
    else:
      msg = correctFmt
    send_msg(msg)
    pass
  elif 'set_telegram_user' in sms.lower():
    correctFmt = 'The correct format is:\n\nSet_telegram_username|username'
    username = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      username = str(splitsms[1].strip())
    except:
      error = 1
    if error == 0:
      if len(username) >= 1:
        subprocess.call(['sudo','/home/pi/Watchman/saveWatchmanConfig.py','username',username])
        msg='Telegram recepient username has been updated.'
      else:
        msg='Please type a valid username.\n'+correctFmt
    else:
      msg = correctFmt
    send_msg(msg)
    pass
  elif 'set_telegram_token' in sms.lower():
    correctFmt = 'The correct format is:\n\nSet_telegram_token|token'
    token = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      token = str(splitsms[1].strip())
    except:
      error = 1
    if error == 0:
      if validate_token(token):
        if checkInternet(REMOTE_SERVER):
          try:
            bot = telepot.Bot(token)
            data = bot.getMe()
            print data
            error = 0
          except:
            error = 1
          if error == 0:
            subprocess.call(['sudo','/home/pi/Watchman/saveWatchmanConfig.py','token',token])
            subprocess.call(['sudo','/home/pi/Watchman/saveWatchmanConfig.py','chatid','1234'])
            subprocess.call(['sudo','/home/pi/Watchman/saveWatchmanConfig.py','username','username'])
            msg = 'Token loaded successfully!!'
          else:
            msg = 'Token was invalid, please confirm token and try again.'
        else:
          msg='Internet connection needed but is not available, check wifi setup.'
      else:
        msg='Please provide a valid token.\n'+correctFmt
    else:
      msg = correctFmt
    send_msg(msg)
    pass
  elif 'configure_sensor' in sms.lower():
    correctFmt = 'The correct format is:\n\nConfigure_sensor|wifi-ssid|password|sensor-ip|gateway-ip'
    ssid = ''
    pswd = ''
    sensorip = ''
    gatewayip = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      ssid = str(splitsms[1].strip())
      pswd = str(splitsms[2].strip())
      sensorip = str(splitsms[3].strip())
      gatewayip = str(splitsms[4].strip())
    except:
      error = 1
    if error == 0:
      if validate_ip(sensorip) and validate_ip(gatewayip):
        if sensorip != gatewayip:
          print 'Sensor IP: '+sensorip
          print 'Gateway IP: '+gatewayip
          #subprocess.call(['sudo','/home/pi/Watchman/configureSensor.py', sensorip, gatewayip])
          msg='Sensor has been configured successfully!'
        else:
          msg = 'Sensor IP and Gateway IP cannot be the same.\n'+correctFmt
      else:
        msg='Please provide valid IP addresses.\n'+correctFmt
    else:
      msg = correctFmt
    send_msg(msg)
    pass
  elif 'set_static_ip' in sms.lower():
    correctFmt = 'The correct format is:\n\nSet_static_IP|gatewayIP|routerIP|dns\ne.g. \nSet_static_IP|192.168.1.10|192.168.1.1|8.8.8.8'
    ip = ''
    router = ''
    dns = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      ip = str(splitsms[1].strip())
      router = str(splitsms[2].strip())
      dns = str(splitsms[3].strip())
    except:
      error = 1
    if error == 0:
      if validate_ip(ip) and validate_ip(router) and (len(dns)>6):
        print 'Gateway IP: '+ip+' Router IP: '+router+' DNS: '+dns
        result = subprocess.check_output(['sudo','/home/pi/Watchman/setStaticIP.py',ip, router, dns])
        print result
        if 'done' in str(result):
          msg='Gateway static IP has been updated. Rebooting device..'
          send_msg(msg)
          subprocess.call(['sudo','reboot'])
        else:
          msg='Error occured please try again'
      else:
        msg='Please provide valid IP addresses.\n'+correctFmt
    else:
      msg = correctFmt
    send_msg(msg)
    pass
  elif 'connect_wifi' in sms.lower():
    correctFmt = 'The correct format is:\n\nConnect_wifi|ssid|password'
    ssid = ''
    pswd = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      ssid = str(splitsms[1].strip())
      pswd = str(splitsms[2].strip())
    except:
      error = 1
    if error == 0:
      if len(ssid) >= 1 and len(pswd) >= 1:
        print 'SSID: '+ssid
        print 'Password: '+pswd
        msg = subprocess.check_output(['sudo','/home/pi/Watchman/connectToWifi.py',ssid, pswd])
      else:
        msg='Please provide valid wifi credentials.\n'+correctFmt
    else:
      msg = correctFmt
    send_msg(msg)
    pass
  elif 'stop' in sms.lower():
    response = updateWifiRegister(0,'*',0,'sendAlert')
    state = response[0]
    if state == '1':
      msg = 'Updates from all sensors have been disabled.\nSend \'Start\' to enable all sensor updates.'
    elif state == 'A':
      msg = 'Updates from all sensors have already been disabled.\nSend \'Start\' to enable all sensor updates.'
    elif state == '0':
      msg = 'There was an error, have you registered any sensors? please try again..'
    else:
      msg = 'Operation failed, please try again..'
    send_msg(msg)
    pass
  elif 'start' in sms.lower():
    response = updateWifiRegister(0,'*',1,'sendAlert')
    state = response[0]
    if state == '1':
      msg = 'Updates from all sensors have been enabled.\nSend \'Stop\' to disable all sensors updates.'
    elif state == 'A':
      msg = 'Updates from all sensors have already been enabled.\nSend \'Stop\' to disable all sensor updates.'
    elif state == '0':
      msg = 'There was an error, have you registered any sensors? please try again..'
    else:
      msg = 'Operation failed, please try again..'
    send_msg(msg)
    pass
  elif 'reboot' in sms.lower():
    send_msg('System will reboot after 1 minute..')
    output = subprocess.Popen(["sudo", "shutdown", "-r"])
  elif 'check_config' in sms.lower():
    msg = subprocess.check_output(['sudo','/home/pi/Watchman/checkConfig.py'])
    msg1 = msg.split('|')[0]
    msg2 = msg.split('|')[1]
    msg3 = msg.split('|')[2]
    send_msg(msg1)
    send_msg(msg2)
    send_msg(msg3)
  elif 'use_gprs' in sms.lower():
    subprocess.Popen(['sudo','/home/pi/Watchman/activateGprs.py'])
  else:
    send_msg('Use the following commands:\n1.Start\n2.Stop\n3.Reboot\n4.Ussd|*144#\n5.Check_config\n6.Show_config_commands\n7.Use_gprs')

def check_incoming():
    if ser.in_waiting:
        buf = ''
        while ser.in_waiting:
          buf+=ser.readline()
        print(buf)
        global _buffer
        buf = convert_to_string(buf)
        _buffer = buf
        params=buf.split(',')
        global savbuf
        savbuf = ''
        global callingAdmin
        #print 'Params: '+params[0]
        if params[0][0:5] == "+CMTI":
            msgid = int(params[1])
            smsdata = read_sms(msgid)
            try:
              sender = smsdata[0]
              sms = smsdata[1]
            except:
              count = 0
              for count in range(5):
                try:
                  print str(count)+'. retrying to read sms no: '+str(params[1])
                  msgid = int(params[1])
                  smsdata = read_sms(msgid)
                  sender = smsdata[0]
                  sms = smsdata[1]
                  if sms:
                    break
                except Exception as e:
                  print 'SMS Error: {}'.format(e)
                count += 1
            if msgid > 65:
              delete_all_sms()
            print sender
            print sms
            global admin
            if len(str(admin)) < 2:
              admin = sender
            if admin[-9:] == sender.strip()[-9:]:
              executeSmsCmd(sms)
            else:
              subprocess.Popen(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(sms),'1'])
            pass
        elif params[0][0:5] == '+CUSD':
            try:
              msg = buf.split('"')
              send_msg(msg[1])
            except Exception as e:
              print("Error: {}".format(e))
            pass
        elif params[0] == "NO CARRIER":
            callingAdmin = False
            pass
        elif ('RING' in params[0]) or (params[0][0:5] == "+CLIP"):
            if not callingAdmin:
              result = command('ATA\r\n')
              if ser.in_waiting:
                result = ser.readline()
              print 'Result '+result
              if 'OK' in result:
                playMsgIfUserCalled()
                command('ATH\r\n')
            pass
        elif params[0] == "MO CONNECTED":
            playMsgIfCallingUser()
            command('ATH\r\n')
            callingAdmin = False
            global msgToAdmin
            msgToAdmin = ''
            pass
        elif "+CMT:" in params[0]:
            print 'Memory full, deleting all messages..'
            if "memory is full" in buf:
              delete_all_sms()
              print 'done'
def exitScript(e = 'Closing Script'):
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print '['+ts+']'+': {}'.format(e)
  c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w+")
  status = c.write('0')
  c.close()
  sys.exit()

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

#######################################################################################
ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print '['+ts+']'
print("Starting checkSim800lEvents script..")
#check if script is already running
try:
  c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  print 'txt file not found, txt file generated..'
  exitScript(e)
if status == '1':
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] checkSim800lEvents already running!!'
  sys.exit()

#check if gprs is activated
try:
  c = open("/home/pi/Watchman/useGprs.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  err = '['+ts+']'+': {}'.format(e)
  print err
  if 'No such file' in err:
    c = open("/home/pi/Watchman/useGprs.txt","w")
    status = c.write('0')
    c.close()
  sys.exit()
if status == '1':
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print'['+ts+'] gprs mode is active..'
  sys.exit()

c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w")
status = c.write('1')
c.close()

try:
  ser=serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2)
except Exception as e:
  exitScript(e)

print 'Looking for Sim800l..'
if alive(10):
  print 'Sim800l is alive..'
else:
  exitScript('No response closing script..')

try:
  broker_address="localhost"
  print("Starting closeCheckSimEvents listener")
  client = mqtt.Client("Sim800lScript") #create new instance
  client.on_message=on_message #attach function to callback
  print("connecting to broker")
  client.connect(broker_address) #connect to broker
  client.loop_start() #start the loop
  #subscribe to interesting topics..
  print("Subscribing to topic","closeCheckSimEvents","sendSMS","callNumber")
  client.subscribe("closeCheckSimEvents")
  client.subscribe("sendSMS")
  client.subscribe("callNumber")

except Exception as e:
  print 'Failed to initialize mqtt listner..'
  exitScript(e)

config = SafeConfigParser()
config.read('/home/pi/Watchman/WatchmanConfig.ini')
admin = ''
reverseCallAdmin = ''
try:
  admin = config.get('ConfigVariables', 'admin_no')
  reverseCallAdmin = config.get('ConfigVariables', 'callback_no')
except:
  print 'Admin No not found..'
config2 = SafeConfigParser()
config2.read('/home/pi/Watchman/sqldb/sqlCredentials.ini')

usr = config2.get('credentials', 'username')
pswd = config2.get('credentials', 'password')
db = config2.get('credentials', 'database')

savbuf = ''
_buffer = ''
sendingSms = False
exit = False
callingAdmin = False
REMOTE_SERVER = 'www.google.com'
msgToAdmin = ''

print 'checkSim800lEvents initialized..'
setup()
#check if we have unread msgs
print 'Checking latest unread message..'
result = command('AT+CMGL="REC UNREAD"\n',5,3000)
if result:
  try:
    unread = savbuf.split('+CMGL:')
    sms = unread[-1].split('\n')[1]
    print 'latest txt: ['+sms+']'
    executeSmsCmd(sms)
  except:
    print 'Error, no unread sms'
else:
  print 'No unread sms'
try:
  while True:
    if exit:
      exitScript('Closing checkSim800lEvents.py script!!')
    check_incoming()
    time.sleep(1)
except Exception as e:
  exitScript(e)
