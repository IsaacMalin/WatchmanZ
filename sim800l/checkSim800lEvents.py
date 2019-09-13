import os,time,sys
import serial
import time

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
            ser=serial.Serial("/dev/serial0", baudrate=9600, timeout=1)
        except Exception as e:
            sys.exit("Error: {}".format(e))

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


savbuf = ''
try:
  ser=serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2)
except Exception as e:
  sys.exit("Error: {}".format(e))
setup()
print 'checkSim800lEvents initialized..'

while True:
  check_incoming()
  time.sleep(1)
