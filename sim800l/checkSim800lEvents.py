#!/usr/bin/env python
import os,time,sys
import serial
import time
import subprocess
import socket
import telepot
from datetime import datetime
import paho.mqtt.client as mqtt
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
            ser=serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2)
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
        #print 'Params: '+params[0]
        if params[0][0:5] == "+CMTI":
            msgid = int(params[1])
            smsdata = read_sms(msgid)
            try:
              sender = smsdata[0]
              sms = smsdata[1]
            except Exception as e:
              print 'Error: {}'.format(e)
              return
            if msgid > 65:
              delete_all_sms()
            print sender
            print sms
            global admin
            if len(str(admin)) < 2:
              admin = sender
            if admin[-9:] == sender.strip()[-9:]:
              splitSms = sms.split('|')
              global callingAdmin
              if 'ssd|' in sms:
                ussd = splitSms[1]
                ussd = ussd.strip()
                send_ussd(ussd)
                pass
              elif 'config_commands' in sms:
                send_msg('Config Commands:\n1.Connect_wifi\n2.Set_admin_number\n3.Set_callback_number\n4.Set_telegram_username\n5.Set_telegram_token\n6.Set_sensorIP\n7.Set_gateway_static_IP')
                pass
              elif 'et_admin_n' in sms:
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
              elif 'et_callback_n' in sms:
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
              elif 'et_telegram_user' in sms:
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
              elif 'et_telegram_token' in sms:
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
              elif 'et_sensorIP' in sms:
                correctFmt = 'The correct format is:\n\nSet_sensorIP|sensor-ip|gateway-ip'
                sensorip = ''
                gatewayip = ''
                msg = ''
                error = 0
                try:
                  splitsms = sms.split('|')
                  sensorip = str(splitsms[1].strip())
                  gatewayip = str(splitsms[2].strip())
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
              elif 'et_gateway_static_' in sms:
                correctFmt = 'The correct format is:\n\nSet_gateway_static_IP|gatewayIP'
                ip = ''
                msg = ''
                error = 0
                try:
                  splitsms = sms.split('|')
                  ip = str(splitsms[1].strip())
                except:
                  error = 1
                if error == 0:
                  if validate_ip(ip):
                    print 'Gateway IP: '+ip
                    #subprocess.call(['sudo','/home/pi/Watchman/setStaticIP.py',ip])
                    msg='Gateway static IP has been updated.'
                  else:
                    msg='Please provide a valid IP address.\n'+correctFmt
                else:
                  msg = correctFmt
                send_msg(msg)
                pass
              elif 'onnect_wifi' in sms:
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
                    msg='Connecting to wifi network..'
                    #subprocess.call(['sudo','/home/pi/Watchman/connectToWifi.py',ssid, pswd])
                  else:
                    msg='Please provide valid wifi credentials.\n'+correctFmt
                else:
                  msg = correctFmt
                send_msg(msg)
                pass

              else:
                send_msg('Use the following commands:\n1.Start\n2.Stop\n3.Reboot\n4.Ussd|*144#\n5.Check_config\n6.Show_config_commands')
            else:
              subprocess.call(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(sms),'0'])
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
def exitScript(e = 'Closing Script'):
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print '['+ts+']'+': {}'.format(e)
  c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w+")
  status = c.write('0')
  c.close()
  sys.exit()

#######################################################################################
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

c = open("/home/pi/Watchman/sim800l/checkSim800lEvents.txt","w")
status = c.write('1')
c.close()

try:
  ser=serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2)
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
savbuf = ''
_buffer = ''
sendingSms = False
exit = False
callingAdmin = False
REMOTE_SERVER = 'www.google.com'
msgToAdmin = ''

print 'checkSim800lEvents initialized..'
setup()
try:
  while True:
    if exit:
      exitScript('Closing checkSim800lEvents.py script!!')
    check_incoming()
    time.sleep(1)
except Exception as e:
  exitScript(e)
