#!/usr/bin/env python
import subprocess

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

def sendPendingMsgs():
  print 'Trying to send pending sms messages to telegram if any..'
  c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","r")
  pendingMsgs = c.read()
  c.close()
  if '~' in pendingMsgs:
    if pingServer('8.8.8.8'):
      p = pendingMsgs.split('~')
      stillPending = ' '
      try:
        print 'Net available, trying to send pending sms..'
        subprocess.call(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py','You have pending sms messages:\n','0'])
        for msg in p:
          print 'Sending a message..'
          result = subprocess.check_output(['sudo','/home/pi/Watchman/TelegramBot/TelegramSendMsg.py',str(msg),'0'])
          print result
          if not 'sent' in result:
            if len(str(msg))>5:
              print 'Message not sent, returning it to pending msgs.'
              if not '`' in msg:
                stillPending += msg+'`~'
        c = open("/home/pi/Watchman/AudioMsgs/pendingMsgs.txt","w")
        c.write(stillPending)
        c.close()
      except Exception as e:
        print 'Error: {}'.format(e)
  else:
    print 'There are no pending messages.'

sendPendingMsgs()
