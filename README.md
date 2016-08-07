# py_lcd_i2c_loves_them_all
Module to interface HD44780-based LCDs through I2C port expanders, like PCF8574T

This module aims to be a complete solution in interfacing with these cute character LCDs.
Original credit goes to [DenisFromHR](https://gist.github.com/DenisFromHR) (Croatia).
I have added few higher-level features such as line wraping, setting array-like access (setting single element. getting not supported :( ).
Be certain to pass dimension of your display as a tuple in instance initialization.

Quick glances and bug reports are welcome.
