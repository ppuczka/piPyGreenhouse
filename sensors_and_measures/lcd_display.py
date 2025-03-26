from datetime import datetime, time
from grove.display.base import *
from grove.i2c import Bus

import logging

import sys

from models import Greenhouse

class LcdDisplay(Display):
    def __init__(self, address = 0x3E, display_interval_sec = 15):
        self._bus = Bus()
        self._addr = address
        self._bus.address(self._addr)
        if self._bus.writeByte(0):
            logging.error(f"Check if the LCD {self.type} inserted, then try again")
            sys.exit(1)
        self.dispaly_interval_sec = display_interval_sec
        logging.info(f"LCD initialized {self.type} type")
        logging.info(f"LCD rows / cols {self.size}")
        logging.info(f"Display interval: {self.dispaly_interval_sec}s")
   
    @property
    def name(self):
        return "Greenhouse"
    
    def type(self):
        return "JHD1802"
    
    def display_greenhouse_info(self, metrics: Greenhouse, uptime: str):
        self.clear()
        self.write(f"Temp: {metrics.air_temperature}C")
        self.setCursor(1, 0)
        self.write(f"Humidity: {metrics.air_humidity}%")
        time.sleep(self.dispaly_interval_sec)
        
        self.clear()
        self.write(f"Moisture: {metrics.soil_moisture}%")
        self.setCursor(1, 0)
        self.write(f"Light: {metrics.light_intensity}")
        time.sleep(self.dispaly_interval_sec)
        
        self.clear()
        self.write("Last updated:")
        self.setCursor(1, 0)
        self.write(metrics.datetime.strftime("%y-%m-%d %H:%M:%S"))

        self.write(f"Uptime: {uptime}")
        time.sleep(self.dispaly_interval_sec)
        
        