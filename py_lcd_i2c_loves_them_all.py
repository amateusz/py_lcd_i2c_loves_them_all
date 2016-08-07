# -*- coding: utf-8 -*-
"""
Copyright (C) 2014-2015 Denis Pleic
Made available under GNU GENERAL PUBLIC LICENSE

# Modified Python I2C library for Raspberry Pi
# as found on http://www.recantha.co.uk/blog/?p=4849
# Joined existing 'i2c_lib.py' and 'lcddriver.py' into a single library
# added bits and pieces from various sources
# By DenisFromHR (Denis Pleic)
# 10-02-2015, ver 0.1

# enhanced printing and line wraping by amateusz (Mateusz Grzywacz)
# 07-08-2016

"""
#
#
import smbus
from time import sleep


class i2c_device:
    def __init__(self, addr, port):
        self.addr = addr
        self.bus = smbus.SMBus(port)

    # Write a single command
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

    # Write a command and argument
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        sleep(0.0001)

    # Write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

    # Read a single byte
    def read(self):
        return self.bus.read_byte(self.addr)

    # Read
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)

    # Read a block of data
    def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)


# LCD Address
ADDRESS = 0x27

# Default dimensions
DIMENSIONS = (16, 2)

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit


class lcd:
    # initializes objects and lcd
    def __init__(self, address=ADDRESS, dimensions=DIMENSIONS, port=1):
        try:
            self.lcd_device = i2c_device(address, port)
            self.dimensions = dimensions

            self.write(0x03)
            self.write(0x03)
            self.write(0x03)
            self.write(0x02)

            self.write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
            self.write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
            self.write(LCD_CLEARDISPLAY)
            self.write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
            sleep(0.2)
        except IOError:
            print 'cannot access i2c device @ ' + hex(address)
            raise

    # clocks EN to latch command
    def clock(self, data):
        '''clock as verb. toggle EN pin to make lcd accept the data'''
        self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
        sleep(.0003)
        self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
        sleep(.000006)

    def write_four_bits(self, data):
        self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
        self.clock(data)

    # write a command to lcd
    def write(self, cmd, mode=0):
        self.write_four_bits(mode | (cmd & 0xF0))
        self.write_four_bits(mode | ((cmd << 4) & 0xF0))

    # write a character to lcd (or character rom) 0x09: backlight | RS=DR<
    # works!
    def write_char(self, charvalue, mode=1):
        self.write_four_bits(mode | (charvalue & 0xF0))
        self.write_four_bits(mode | ((charvalue << 4) & 0xF0))

    # put string function
    def display(self, string, line=0):
        self.display_exact(string, line, 0)

    # clear lcd and set to home
    def clear(self):
        self.write(LCD_CLEARDISPLAY)
        self.write(LCD_RETURNHOME)

    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def backlight(self, state):  # for state, 1 = on, 0 = off
        if state == 1:
            self.lcd_device.write_cmd(LCD_BACKLIGHT)
        elif state == 0:
            self.lcd_device.write_cmd(LCD_NOBACKLIGHT)

    # add custom characters (0 - 7)
    def load_custom_chars(self, fontdata):
        self.write(0x40);
        for char in fontdata:
            for line in char:
                self.write_char(line)

    # define precise positioning (addition from the forum)
    def display_exact(self, string, line, pos):  # main printing function
        '''print string. line and pos are indexed[0]'''
        if line > self.dimensions[1] - 1 or pos > self.dimensions[0] - 1: return

        if len(string) + pos > self.dimensions[0]:
            # string = string[:len(self)]
            string, rest = string[:self.dimensions[0] - pos], string[self.dimensions[0] - pos:]
            self.display(rest,
                         line + 1)  # recursive thing =^.^=  it displays lines in reverse order, but it doesn't matter as long as everything works and they don't overlap

        if line == 0:
            pos_new = pos
        elif line == 1:
            pos_new = 4 * 16 + pos
        elif line == 2:
            pos_new = self.dimensions[0] + pos
        elif line == 3:
            pos_new = 4 * 16 + self.dimensions[0] + pos

        self.write(0x80 + pos_new)

        for char in string:
            self.write(ord(char), Rs)

    def __len__(self):
        return self.dimensions[0] * self.dimensions[1]

    def __setitem__(self, key, value):
        assert key < self.__len__()
        # transform linear lenght data info x,y on array
        line, pos = divmod(key, self.dimensions[0])

        self.display_exact(value, line, pos)
