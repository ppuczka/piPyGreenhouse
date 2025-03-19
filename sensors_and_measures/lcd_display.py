import logging
from grove.lcd.sh1107g import *

import sys

class LcdDisplay(JHD1802):
    def __init__(self, address = 0x3E):
        self._bus = mraa.I2c(0)
        self._addr = address
        self._bus.address(self._addr)
        if self._bus.writeByte(0):
            logging.info(f"Check if the LCD {self.type} inserted, then try again")
            sys.exit(1)
        self.jhd = upmjhd.Jhd1313m1(0, address, address)

    @property
    def name(self):
        return "Greenhouse"
    
    def type(self):
        return "JHD1802"