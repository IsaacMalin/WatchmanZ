#!/usr/bin/python3
import board
import digitalio
import adafruit_ssd1306

WIDTH = 128
HEIGHT = 64     # Change to 64 if needed
BORDER = 1

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

# Clear display.
oled.fill(0)
oled.show()

