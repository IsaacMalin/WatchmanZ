#!/usr/bin/env python
import os,time,sys
import serial
import time
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
      msg = msg.split('^')
      destno = msg[0]
      msgtext = msg[1]
      print 'Sending SMS to '+destno
      result = send_sms(destno,msgtext)
      #if not 'OK' in result:
        #callAdmin()
    elif topic == 'callNumber':
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
                return  [number,date,time,savbuf]
    return None

def call_number(num):
    command('AT+MORING=1\r\n')
    command('ATD'+str(num)+';\r\n')

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

def check_incoming():
    if ser.in_waiting:
        buf=ser.readline()
        print(buf)
        buf = convert_to_string(buf)
        params=buf.split(',')

        if params[0][0:5] == "+CMTI":
            msgid = int(params[1])
            print read_sms(msgid)
            if msgid > 65:
              delete_all_sms()
            pass
        elif params[0] == "NO CARRIER":

            pass
        elif params[0] == "RING" or params[0][0:5] == "+CLIP":
            #@todo handle
            pass
def exitScript(e = 'Closing Script'):
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print '['+ts+']'+e
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
