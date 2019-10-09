import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

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

# Draw a white background
#draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Draw a smaller inner rectangle
#draw.rectangle((BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
#               outline=0, fill=0)


draw.line((0, 16, oled.width-1, 16), fill=255)
draw.line((0, 40, oled.width-1, 40), fill=255)
draw.line((32, 41, 32, 64), fill=255)
draw.line((0, 52, 32, 52), fill=255)

# Load default font.
#font = ImageFont.load_default()

serif1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 14)
serif2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 10)
sans1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
sans2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
# Draw Some Text
#text = "Hello World!"
#(font_width, font_height) = font.getsize(text)
#draw.text((oled.width//2 - font_width//2, oled.height//2 - font_height//2),
#          text, font=font, fill=255)

draw.text((1, 0), 'GSM Ready', font=sans1, fill=255)
draw.text((1, 20), 'No Sensor Msg!!', font=sans2, fill=255)
draw.text((1, 42), 'WiFi', font=serif2, fill=255)
draw.text((36, 42), 'Not Connected', font=sans2, fill=255)
draw.text((1, 54), 'Batt', font=serif2, fill=255)
draw.text((36, 54), 'Not Detected', font=sans2, fill=255)

# Display image
oled.image(image)
oled.show()

