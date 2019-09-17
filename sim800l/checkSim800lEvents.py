#!/usr/bin/env python
import os,time,sys
import serial
import time
import subprocess
import socket
from datetime import datetime
import paho.mqtt.client as mqtt

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
    return result

def send_sms(destno,msgtext):
    result = command('AT+CMGS="{}"\n'.format(destno),99,5000,msgtext+'\x1A')
    if result and result=='>' and savbuf:
        params = savbuf.split(':')
        if params[0]=='+CUSD' or params[0] == '+CMGS':
            return 'OK'
    return 'ERROR'

def send_msg(msg):
    print 'Sending SMS..'
    result = send_sms(admin,msg)
    if not 'OK' in result:
      print 'failed, calling admin..'
      global msgToAdmin
      msgToAdmin = "Sending text message failed. Airtime balance may be depleted. Try loading more airtime."
      command('\r\n')
      if alive():
        call_number(reverseCallAdmin)
      else:
        print 'Error in GSM Module'
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

def alive():
    for x in range(1,6):
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
        buf=ser.readline()
        print(buf)
        buf = convert_to_string(buf)
        params=buf.split(',')

        if params[0][0:5] == "+CMTI":
            msgid = int(params[1])
            smsdata = read_sms(msgid)
            sender = smsdata[0]
            print sender
            sms = smsdata[1]
            global savbuf
            savbuf = ''
            if msgid > 65:
              delete_all_sms()
            print sms
            if admin[-9:] == sender.strip()[-9:]:
              splitSms = sms.split('|')
              if 'ssd|' in sms:
                ussd = splitSms[1]
                ussd = ussd.strip()
                send_ussd(ussd)
              else:
                send_msg('Use the following commands:\n1.Ussd|*144# - Check Balance')
            else:
              subprocess.call(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(sms),'1'])
            pass
        elif params[0][0:5] == '+CUSD':
            try:
              send_msg(params[1])
            except Exception as e:
              print("Error: {}".format(e))
            pass
        elif params[0] == "NO CARRIER":

            pass
        elif params[0] == "RING" or params[0][0:5] == "+CLIP":
            if not callingAdmin:
              result = command('ATA\r\n')
              if 'OK' in result:
                playMsgIfUserCalled()
                command('ATH\r\n')
            pass
        elif params[0] == "MO CONNECTED":
            playMsgIfCallingUser()
            command('ATH\r\n')
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
  ser=serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2)
except Exception as e:
  exitScript(e)

print 'Looking for Sim800l..'
if alive():
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

savbuf = ''
exit = False
callingAdmin = False
REMOTE_SERVER = 'www.google.com'
admin = '0723942375'
reverseCallAdmin = '#0723942375'
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
