# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject tod the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
import threading
from math import floor
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi hardware SPI config:
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0

class _Getch:
    """
    Gets a single character from standard input.  Does not echo to
    the screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchMacCarbon()
            except(AttributeError, ImportError):
                self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()
class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt #see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()
class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

#Load default font
font = ImageFont.load_default()

# Hardware SPI usage:
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))

# Initialize library.
disp.begin(contrast=30)

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a white filled box to clear the image.
draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)

tam1 = """00000000000000111100000
00001111000000111110000
00001111100001111110000
00011111100001111110000
00011111111111111111000
00011111111111111111000
00011111111111111111000
00111111111111111111000
00111111111111111111100
01001111000000011111110
01100000011110000000010
10110000111101000000001
10110000111110100000001
10110000111110100000001
10110000111110100000001
01110000011100100000001
01100000001111000000010
00100101000000000000010
00010011000000000000100
00001100000000000011110
00000011111111111100001
00000100000000000000001
00001000000000000011110
00001001000000000010000
00000111000000000010000
00000001000000000011100
00000010000000000100010
00000100000111111000010
00000100011000000111100
00000011100000000000000"""

tam2 = """00000000111110000000000
00000001111111000000000
00000001111111100000000
00000001111111100000000
00000001111111100000000
00000011111111111000000
00001111111111111110000
00011111111111111111000
00110111111111111111100
01000000000000111111110
01000011110000000000010
10000111001000000000001
10000111100100000000001
10000111100100000000001
10000111100100000000001
10000011101000000000001
10000001110000000000010
01000100000000000000010
00100100000000000000100
00011000000000000011000
00000111111111111100000
00000001000000001000000
00000001000001000100000
00000001000100100100000
00000001000100100010000
00000001000100100010000
00000001000011000010000
00000000100000000100000
00000000111100011000000
00000000100100010000000
00000000100100010000000
00000000011011100000000"""

tam3 = """00000000000000000000000
00000011110000000000000
00000111111000011110000
00000111111100111111000
00000111111100111111000
00001111111111111111100
00001111111111111111100
00111111111111111111100
00111111111111111111100
01110000000111111111110
01111000000000000000010
10110100000000000000001
10110100000000000000001
10110100000000000000001
10110100000000000000001
10011000000000000000001
01000000000000000000010
00100000000000000000010
00011000000000000000100
00000110000000000001000
00000001111111111110000
00000001001100000100000
00000001010000000100000
00000010010001000010000
00000010001110000010000
00000010000000000010000
00000010000000000001000
00000100000000000001000
00000100011111111001000
00000100100000000110000
00000011000000000000000
00000000000000000000000"""

tam1a = tam1.split('\n')
tam2a = tam2.split('\n')
tam3a = tam3.split('\n')
draw = ImageDraw.Draw(image)
#draw.point((4,4),fill=0)

key = "lol"
getch = _Getch()
def thread1():
    global key
    lock = threading.Lock()
    while True:
        with lock:
            key = getch()
threading.Thread(target = thread1).start()

#jump variables 
dist = 0
gup = False

#obstacle variables
xx = 0

#other variables
ind = 1
score = 0;
extraspeed = 0;

while True:
    draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
    #clear image
    draw.text((0,0),str(score),font=font)
    extraspeed = floor(score / 100)
    if extraspeed > 10:
        extraspeed = 10
    score += 3
    draw.rectangle((xx,32,xx+3,42),outline=0,fill=0)
    xx = xx + 4 +extraspeed
    if xx >= 84:
        xx = -4;
    if key == ' ':
        if dist == 0:
            gup = True
            key = "lol"
        else:
            key = "lol"
    if gup == True:
        if dist != 12:
            dist += 3
        else:
            gup = False
    else:
        if dist > 0:
            dist -= 3
        else:
            dist = 0

    if ind == 1:
        i = 12-dist #top left corner of drawn sprite y
        j = 60 #top left corner of drawn sprite x
        for line in tam1a:
            for c in line:
                if c == '1':
                    draw.point((j,i),fill=0)
                j+=1
            i+=1
            j=60 #make same as j at start
    if ind == 2:
        i = 12-dist #top left corner of drawn sprite y
        j = 60 #top left corner of drawn sprite x
        for line in tam2a:
            for c in line:
                if c == '1':
                    draw.point((j,i),fill=0)
                j+=1
            i+=1
            j=60 #make same as j at start
    if ind == 3:
        i = 12-dist #top left corner of drawn sprite y
        j = 60 #top left corner of drawn sprite x
        for line in tam3a:
            for c in line:
                if c == '1':
                    draw.point((j,i),fill=0)
                j+=1
            i+=1
            j=60 #make same as j at start
            
    ind += 1
    if ind == 4:
        ind = 1
    draw.line((0,43,83,43),fill=0)
    draw.line((0,44,83,44),fill=0)
    if xx >= float(67) and xx<= float(80) and dist <= 7:
        break

# Display image.
    disp.image(image)
    disp.display()

    time.sleep(0.2)
draw.text((40,10),'Hit',font=font)
disp.image(image)
disp.display()
