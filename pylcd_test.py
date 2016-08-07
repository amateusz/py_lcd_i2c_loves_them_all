import keyword
import random
import string
from time import sleep

import py_lcd_i2c_loves_them_all

try:
    dimensions = (16, 4)
    display = py_lcd_i2c_loves_them_all.lcd(0x21, dimensions)

    for i in range(8):
        display.display_exact(random.choice(keyword.kwlist), random.randrange(dimensions[1]),
                              random.randrange(dimensions[0]))
        sleep(.6)
    sleep(2)
    display.clear()

    for i in range(18):
        display[random.randrange(len(display))] = random.choice(string.ascii_letters)
        display[len(display) - len(str(i)) - len(' ')] = ' ' + str(i)
        sleep(.2)
    sleep(2)
    display.clear()

    while True:
        allChars = list(range(len(display)))
        random.shuffle(allChars)
        while allChars:
            display[allChars.pop()] = random.choice(('0', 'x', '1'))
            sleep(.3)
            # print allChars
        display.clear()
except IOError:
    print 'error connecting to display. address correct ?'
