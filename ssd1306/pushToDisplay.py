#!/usr/bin/python3
import board
import digitalio
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import sys
import time
from configparser import SafeConfigParser
import paho.mqtt.client as mqtt


config = SafeConfigParser(interpolation = None)

def on_message(client, userdata, message):
    mqtt_msg = str(message.payload.decode("utf-8"))
    topic = message.topic
    qos = message.qos
    retainFlag = message.retain
    print("message received " ,mqtt_msg)
    #print("message topic=",topic)
    #print("message qos=",qos)
    #print("message retain flag=",retainFlag)

    #get arguments
    msg = mqtt_msg.split('~')[1]
    section = mqtt_msg.split('~')[0]

    config.read('/home/pi/Watchman/ssd1306/displayData.ini')
    if not config.has_section('messages'):
      config.add_section('messages')
    config.set('messages', str(section), str(msg))

    with open('/home/pi/Watchman/ssd1306/displayData.ini', 'w+') as configfile:
        config.write(configfile)
        configfile.close()

    #get diplay messages..
    try:
      config.read('/home/pi/Watchman/ssd1306/displayData.ini')

      gsm_msg = config.get('messages', '1')
      sensor_msg1 = config.get('messages', '2')
      sensor_msg2 = config.get('messages', '3')
      ssid_msg = config.get('messages', '4')
      batt_msg = config.get('messages', '5')

      # Draw a black filled box to clear the image.
      draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)

      # Draw lines
      draw.line((0, 16, oled.width-1, 16), fill=255)
      draw.line((0, 40, oled.width-1, 40), fill=255)
      draw.line((32, 41, 32, 64), fill=255)
      draw.line((0, 52, 32, 52), fill=255)

      # Draw Some Text
      draw.text((1, 0), gsm_msg, font=sans1, fill=255)
      draw.text((1, 18), sensor_msg1, font=sans2, fill=255)
      draw.text((1, 28), sensor_msg2, font=sans2, fill=255)
      draw.text((1, 42), 'WiFi', font=serif2, fill=255)
      draw.text((36, 42), ssid_msg, font=sans2, fill=255)
      draw.text((1, 54), 'Batt', font=serif2, fill=255)
      draw.text((36, 54), batt_msg, font=sans2, fill=255)

      # Display image
      oled.image(image)
      oled.show()
    except Exception as e:
      print('failed: {}'.format(e))

def exitScript(e = 'Closing Script'):
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print('['+ts+']'+': {}'.format(e))
  c = open("/home/pi/Watchman/ssd1306/pushToDisplay.txt","w+")
  status = c.write('0')
  c.close()
  # Clear display.
  oled.fill(0)
  oled.show()
  sys.exit()

#######################################################################################
ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print('['+ts+']')
print("Starting pushToDisplay script..")
#check if script is already running
try:
  c = open("/home/pi/Watchman/ssd1306/pushToDisplay.txt","r")
  status = c.read()
  status = status.strip()
  c.close()
except Exception as e:
  print('txt file not found, txt file generated..')
  c = open("/home/pi/Watchman/ssd1306/pushToDisplay.txt","w+")
  c.write(' ')
  c.close()
  sys.exit()
if status == '1':
  ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
  print('['+ts+'] pushToDisplay already running!!')
  sys.exit()
c = open("/home/pi/Watchman/ssd1306/pushToDisplay.txt","w")
status = c.write('1')
c.close()

# Initialize Mqtt
try:
  broker_address="localhost"
  print("Starting pushToDisplay listener")
  client = mqtt.Client("pushToDisplayScript") #create new instance
  client.on_message=on_message #attach function to callback
  print("connecting to broker")
  client.connect(broker_address) #connect to broker
  client.loop_start() #start the loop
  #subscribe to interesting topics..
  print("Subscribing to topic","pushToDisplay")
  client.subscribe("pushToDisplay")

except Exception as e:
  print('Error starting mqtt: '.format(e))
  exitScript(e)

# Define the Reset Pin
#oled_reset = digitalio.DigitalInOut(board.D4)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64     # Change to 64 if needed
BORDER = 1

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

serif1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 14)
serif2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 10)
sans1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
sans2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)


try:
  while True:
    time.sleep(1)
except Exception as e:
  exitScript(e)
