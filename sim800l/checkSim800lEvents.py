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
    #print("message topic=",topic)
    #print("message qos=",qos)
    #print("message retain flag=",retainFlag)
    if topic == 'closeCheckSimEvents':
      global exit
      exit = True
    elif topic == 'sendSMS':
      global sendingSms
      print 'Another sms is currently being sent: '+str(sendingSms)
      count = 0
      while sendingSms and count<20:
        print 'Another sms is being sent, waiting..'
        count += 1
        time.sleep(1)
      send_msg(msg)
      subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])
    elif topic == 'callNumber':
      global callingAdmin
      callingAdmin = True
      print 'Calling Number '+msg
      call_number(msg)
      subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])

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
  command('AT+CREG=1\n',lines=3)    # enable to show network status

def command(cmdstr, lines=1, waitfor=500, msgtext=None):
    while ser.in_waiting:
        ser.readline()
    try:
      ser.write(cmdstr.encode())
    except Exception as e:
      print 'Encode cmdstr error: {}'.format(e)
    if msgtext:
        try:
          ser.write(msgtext.encode())
        except Exception as e:
          print 'Encode msgtext error: {}'.format(e)
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
      try:
        ser.write(msgtext.encode()+'\x1A\r\n')
      except Exception as e:
        print 'Encode send_sms msgtext error: {}'.format(e)
      buf = ''
      for x in range(20):
        if x > 18:
          sendingSms = False
          return 'timeout'
        buf = ser.readline()
        if '+CMTI:' in buf:
          _buffer = buf
        print str(x)+'. Waiting for response _buffer: '+str(_buffer)+' buf: '+str(buf)
        time.sleep(1)
        if (('ERROR' in _buffer) or ('ERROR' in buf)):
          sendingSms = False
          return 'error'
        if '+CMGS:' in _buffer or '+CUSD:' in _buffer or '+CMGS:' in buf or '+CUSD:' in buf:
          sendingSms = False
          return 'OK'
      return 'Error'
      #result = command('AT+CMGS="{}"\n'.format(destno),99,5000,msgtext+'\x1A')
    else:
      resetSim800l()
      sendingSms = False
      return 'No Response'

def resetSim800l():
  subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
  time.sleep(10)
  setup()

def send_msg(msg):
    global admin
    global _buffer
    print 'Sending SMS..'
    if admin:
      subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','Sending SMS..','1'])
      result = send_sms(admin,msg)
      print 'send sms result: '+str(result)
      if not 'OK' in result:
        subprocess.call(['/home/pi/Watchman/ssd1306/display.py','Send SMS Failed','1'])
        c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","w+")
        c.write(msg)
        c.close()
        p = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","a+")
        p.write(msg+'~ ')
        p.close()
        print 'failed, calling admin..'
        global msgToAdmin
        msgToAdmin = "Sending text message failed. Airtime balance may be depleted. Try loading more airtime."
        if alive(6):
          if len(str(reverseCallAdmin)) > 2:
            call_number(reverseCallAdmin)
        else:
          print 'No GSM Module found!!'
          resetSim800l()
      else:
        print 'SMS sent!'
        #subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])
        command('AT\n',lines = 3)
      if '+CMTI:' in _buffer:
        act_on_incoming(_buffer)
        _buffer = ''

def send_ussd(ussd):
  result = command('AT+CUSD=1,\"'+str(ussd)+'\",15\r')
  if 'OK' in result:
    return True
  else:
    return False

def read_sms(id):
    global savbuf
    command('AT+CMGF=1\n',lines = 3)
    result = command('AT+CMGR={}\n'.format(id),99)
    if result:
        print 'Reading sms from memory result: '+result
        params=result.split(',')
        if not params[0] == '':
            params2 = params[0].split(':')
            if params2[0]=='+CMGR':
                try:
                  number = params[1].replace('"',' ').strip()
                  date   = params[3].replace('"',' ').strip()
                  time   = params[4].replace('"',' ').strip()
                  #return  [number,date,time,savbuf]
                except:
                  return None
                print 'savbuf buffer: '+savbuf
                return [number,savbuf]
    return None

def call_number(num):
    msg = 'Call:'+num
    print msg
    subprocess.call(['/home/pi/Watchman/ssd1306/display.py',str(msg),'1'])
    command('AT+MORING=1\r\n')
    command('ATD'+num+';\r\n')

def alive(n):
    for x in range(1,n+1):
      if x == 5:
        resetSim800l()
      print str(x)+' checking sim800l..'
      try:
        result = command('AT\n')
      except Exception as e:
        subprocess.call(['sudo','/home/pi/Watchman/sim800l/resetSim800l.py'])
        exitScript(e)
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

def pingServer(hostname):
  print 'pinging '+hostname
  try:
    result = subprocess.check_output(['sudo','ping','-c','2',hostname])
    #print result
    if 'bytes from '+hostname in result:
      print 'net available'
      return True
    else:
      print 'net not available'
      return False
  except Exception as e:
     print 'error, net not available'
     print 'Error: {}'.format(e)
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
  print 'Admin has been called, now playing pending message'
  try:
    c = open("/home/pi/Watchman/AudioMsgs/firstCallingMsg.wav","r")
    c.close()
  except:
    subprocess.call(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/firstCallingMsg.wav','Sending text messages to you failed. Please check airtime balance.'])
  immediateMsg = 'You have no pending messages, '
  try:
    c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","r")
    msg = c.read()
    c.close()
    if len(msg) > 2:
      if 'reports' in msg:
        immediateMsg = 'You have a new message, '+msg+', '
      else:
        immediateMsg = 'You have some pending messages, '
  except:
    c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","w+")
    c.write(' ')
    c.close()
  lastMsg = 'Thank you for your time and have a nice day.'
  subprocess.Popen(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/secondCallingMsg.wav',immediateMsg+lastMsg])
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/firstCallingMsg.wav'])
  subprocess.call(['sudo','aplay','/home/pi/Watchman/AudioMsgs/secondCallingMsg.wav'])
  #Clear text file once the message has been played to user
  c = open("/home/pi/Watchman/AudioMsgs/immediateMsg.txt","w")
  c.write('0')
  c.close()
  sendPendingMsgs()

#method to play audio message if admin calls us
def playMsgIfUserCalled():
  try:
    c = open("/home/pi/Watchman/AudioMsgs/firstCalledMsg.wav","r")
    c.close()
  except:
    subprocess.call(['sudo','pico2wave','-w','/home/pi/Watchman/AudioMsgs/firstCalledMsg.wav','Hello, how are you, the system will update you shortly.'])
  print 'Admin called us, now playing status and pending messages'
  sendPendingMsgs()
  #check if we have pending messages..
  pendingMsg = 'You have no pending messages, '
  try:
    c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","r")
    msg = c.read()
    c.close()
    if len(msg) > 2:
      pendingMsg = 'You have some pending messages, I will send them to you now, '
  except:
    c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","w+")
    c.write(' ')
    c.close()

  #check the battery status and if we are running on mains power or battery power
  battMsg = 'Power source and battery status is unknown, '
  try:
    b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","r")
    msg = b.read()
    if len(msg) > 4:
      splitMsg = msg.split('#')
      source = splitMsg[0]
      level = splitMsg[1]
      sourceMsg = 'The system is running on mains power. '
      if(source == '1'):
        sourceMsg = 'The system is running on battery power. '
      battMsg = sourceMsg+'The battery level is, '+level+'.  '
    b.close()
  except:
    b = open("/home/pi/Watchman/AudioMsgs/batteryStatus.txt","w+")
    b.write(' ')
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

  #Clear text file once the message has been played to user (pending msgs will be cleared once they are sent via telegram)
  #c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","w")
  #c.write('0')
  #c.close()

def executeSmsCmd(sms):
  splitSms = sms.split('|')
  if 'ussd|' in sms.lower():
    ussd = splitSms[1]
    ussd = ussd.strip()
    send_ussd(ussd)
    pass
  elif 'show_config_commands' in sms.lower():
    send_msg('Config Commands:\n1.Connect_wifi\n2.Set_admin_number\n3.Set_callback_number\n4.Set_telegram_username\n5.Set_telegram_token\n6.Set_static_IP\n7.Read_sensor\n8.Configure_sensor')
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
  elif 'read_sensor' in sms.lower():
    try:
      print 'Reading Sensor..'
      msg=subprocess.check_output(['sudo','/home/pi/Watchman/readSensor.py'])
    except:
      msg = 'Error reading sensor, please try again'
    send_msg(msg)
    pass
  elif 'configure_sensor' in sms.lower():
    correctFmt = 'The correct format is:\n\nConfigure_sensor|sensor_name|wifi_ssid|password|sensor_ip|gateway-hub_ip|router_ip'
    name = ''
    ssid = ''
    pswd = ''
    sensorip = ''
    gatewayip = ''
    routerip = ''
    msg = ''
    error = 0
    try:
      splitsms = sms.split('|')
      name = str(splitsms[1].strip())
      ssid = str(splitsms[2].strip())
      pswd = str(splitsms[3].strip())
      sensorip = str(splitsms[4].strip())
      gatewayip = str(splitsms[5].strip())
      routerip = str(splitsms[6].strip())
      print 'Sensor_Name:'+name
      print 'Sensor IP: '+sensorip
      print 'Gateway-hub IP: '+gatewayip
      print 'Router IP:'+routerip
    except:
      error = 1
    if error == 0:
      if validate_ip(sensorip) and validate_ip(gatewayip) and validate_ip(routerip):
        if sensorip != gatewayip and sensorip != routerip and routerip != gatewayip:
          if len(name)>=1 and len(name)<=15:
            if len(ssid)>=1 and len(ssid)<=15:
              if len(pswd)>=1 and len(pswd)<=15:
                print 'Configuring sensor..'
                try:
                  msg = subprocess.check_output(['sudo','/home/pi/Watchman/configureSensor.py', name, ssid, pswd, sensorip, gatewayip, routerip])
                except:
                  msg='Error configuring sensor, please try again'
              else:
                msg='Please provide WiFi password (15 characters maximum)'
            else:
              msg='Please provide WiFi ssid (15 characters maximum)'
          else:
            msg='Please provide a sensor name (15 charaters maximum)'
        else:
          msg = 'IP addresses cannot be similar.\n'+correctFmt
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
    global checkingIncoming
    checkingIncoming = True
    if ser.in_waiting:
        buf = ''
        while ser.in_waiting:
          buf+=ser.readline()
        if len(str(buf))>1:
          act_on_incoming(buf)
        else:
          print 'got ['+str(buf)+'] from sim800l, checking if alive..'
          if alive(4):
            setup()
    checkingIncoming = False


def sendPendingMsgs():
  subprocess.Popen(['sudo','/home/pi/Watchman/AudioMsgs/sendPendingMsgs.py'])

def act_on_incoming(buf):
    if buf:
        print('Got incoming from sim800l: ['+str(buf))+']'
        global _buffer
        global admin
        buf = convert_to_string(buf)
        _buffer = buf
        params=buf.split(',')
        global savbuf
        savbuf = ''
        global callingAdmin
        #print 'Params: '+params[0]
        if params[0][0:5] == "+CMTI":
            subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','Got New SMS..','1'])
            if params[1] != None:
              msgid = int(params[1])
              smsdata = read_sms(msgid)
              sender = ''
              sms = ''
              try:
                sender = smsdata[0]
                sms = smsdata[1]
              except:
                for count in range(10):
                  if count > 8:
                    exitScript('fatal error refreshing script!!')
                  try:
                    print str(count)+'. retrying to read sms no: '+str(params[1])
                    if count == 4:
                      resetSim800l()
                      time.sleep(5)
                    msgid = int(params[1])
                    smsdata = read_sms(msgid)
                    sender = smsdata[0]
                    sms = smsdata[1]
                    if len(sms) > 2:
                      break
                  except Exception as e:
                    print 'SMS Error: {}'.format(e)
                  count += 1
              if msgid > 65:
                delete_all_sms()
              #print sender
              #print sms
              if len(str(admin)) < 2:
                admin = sender
              if admin[-9:] == sender.strip()[-9:]:
                executeSmsCmd(sms)
              else:
                if sms:
                  print 'Trying to send msg: '+str(sms)+' via Telegram..'
                  subprocess.Popen(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(sms),'1'])
                  sendPendingMsgs()
            subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])
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
              #print 'Result '+result
              if 'OK' in result:
                subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','Call Ongoing..','1'])
                playMsgIfUserCalled()
                command('ATH\r\n')
              subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])
            pass
        elif params[0] == "MO CONNECTED":
            subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','TALKING..','1'])
            playMsgIfCallingUser()
            command('ATH\r\n')
            callingAdmin = False
            global msgToAdmin
            msgToAdmin = ''
            subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])
            pass
        elif "+CMT:" in params[0]:
            print 'Memory full, deleting all messages..'
            if "memory is full" in buf:
              delete_all_sms()
              print 'done'
        #subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])

def exitScript(e = 'Closing Script'):
  subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Paused','1'])
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

def checkUnreadMsgs():
    print 'Checking latest unread message..'
    global checkingUnread
    checkingUnread = True
    global savbuf
    global sendingSms
    if sendingSms:
      print 'Sending sms in progess..'
    else:
      print 'No sms is being sent, proceeding..'
    try:
      count = 0
      while sendingSms and count<10:
        count += 1
        print str(count)+'. Another sms is being sent, chillin..'
        time.sleep(2)

      checkError = 0
      no = ''
      sms = ''

      result = command('AT+CMGL="REC UNREAD"\n',65,5000)
      #print '/savbuf {'+savbuf+'} /savbuf'
      if result:
        try:
          savbuf = result+'\n'+savbuf
          unread = savbuf.split('+CMGL:')
          #print '/unread {'
          #print '\n'.join(unread)
          #print '} /unread'
          #print '['+unread[-1]+']'
          sms = unread[-1].split('\n')[1]
          try:
            no = unread[-1].split('"')[3]
            print 'latest txt: ['+sms+'] from: '+str(no)
          except:
            checkError = 1
          if checkError == 0:
            if admin[-9:] == no.strip()[-9:]:
              print 'Executing sms cmd from admin..'
              executeSmsCmd(sms)
            else:
              if sms:
                print 'Trying to send msg: '+str(sms)+' via Telegram..'
                subprocess.Popen(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(sms),'1'])
          else:
            print 'No unread sms found!'
        except Exception as e:
          print 'Error, {}'.format(e)
      else:
        print 'No unread sms'
    except Exception as e:
      print 'Error: {}'.format(e)
      checkingUnread = False
    checkingUnread = False
    subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])

def checkNetStatus():
  result = command('AT+CREG?\n',lines = 3)
  print 'Checking network status..'
  try:
    state = result.split(',')[1]
    state = state.split('\n')[0]
    state = state.strip()
    print 'status: {}'.format(state)
    if state == '0':
      return 'GSM: Unregistered'
    elif state == '1':
      return 'GSM: Registered'
    elif state == '2':
      return 'GSM: Searching'
    elif state == '3':
      return 'GSM: Denied'
    elif state == '4':
      return 'GSM: Unknown'
    elif state == '5':
      return 'GSM: Roaming'
    else:
      return 'GSM: Error'
  except Exception as e:
    print 'Error checking net status: {}'.format(e)
    return 'GSM: Error'

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
  subprocess.call(['/home/pi/Watchman/ssd1306/display.py','Initializing GSM','1'])
  print 'Sim800l is alive..'
else:
  subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py','No GSM Module','1'])
  exitScript('No response closing script..')

#subprocess.call(['/home/pi/Watchman/ssd1306/display.py','GSM Ready','1'])
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
checkingIncoming = False
exit = False
callingAdmin = False
REMOTE_SERVER = 'www.google.com'
msgToAdmin = ''

print 'checkSim800lEvents initialized..'
setup()
#check if we have unread msgs
time.sleep(15)
checkingUnread = False
checkUnreadMsgs()
subprocess.call(['sudo','poff','rnet'])

try:
  count = 0
  while True:
    count += 1
    if exit:
      exitScript('Closing checkSim800lEvents.py script!!')
    if count > 300:
      print 'checking if sim800l is alive..'
      while sendingSms and checkingIncoming and count < 320:
        print str(count)+'Waiting for sendingSms: '+sendingSms+' and checkIncoming:  '+checkingIncoming
        count += 1
        time.sleep(1)
      if not alive(10):
        exitScript('No response from GSM Module, killing script..')
      netStatus = checkNetStatus()
      if not 'GSM: Reg' in netStatus:
        subprocess.Popen(['/home/pi/Watchman/ssd1306/display.py',str(netStatus),'1'])
      print netStatus
      if 'Error' in netStatus:
        print 'Error checking network status..'
        resetSim800l()
      count = 0
    check_incoming()
    time.sleep(1)
except:
  exitScript()
