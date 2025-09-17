from datetime import datetime, time
from grove.display.jhd1802 import *
from grove.i2c import Bus
import time
import logging

import sys

from models import Greenhouse

class LcdDisplay(JHD1802):
    def __init__(self, address = 0x3E, display_interval_sec = 5):
        self._bus = Bus()
        self._addr = address
        if self._bus.write_byte(self._addr, 0):
            logging.error(f"Check if the LCD inserted, then try again")
            sys.exit(1)
        self.dispaly_interval_sec = display_interval_sec
        self.textCommand(0x02)
        time.sleep(0.1)
        self.textCommand(0x08 | 0x04) # display on, no cursor
        self.textCommand(0x28)
        logging.info(f"LCD initialized ")
        logging.info(f"Display interval: {self.dispaly_interval_sec}s")
        self.clear()
        self.home()
        self.write("Initializing ...")
        time.sleep(1)
        
    @property
    def name(self):
        return "Greenhouse"
    
    def type(self):
        return "JHD1802"
    
    def status(self):
        self.clear()
        self.home()
        self.write("PiGreenhouse")
        self.setCursor(1, 0)
        self.write("Initialized")
        time.sleep(self.dispaly_interval_sec)

    def display_greenhouse_info(self, metrics: Greenhouse, uptime: str):
        self.clear()
        self.home()
        self.write(f"Temp: {metrics.air_temperature.temperature}C")
        self.setCursor(1, 0)
        self.write(f"Humidity: {metrics.air_humidity.humidity}%")
        time.sleep(self.dispaly_interval_sec)
        
        self.clear()
        self.home()
        self.write(f"Soil moisture: {metrics.soil_moisture.soil_moisture}%")
        self.setCursor(1, 0)
        self.write(f"Light: {metrics.light_intensity.intensity}")
        time.sleep(self.dispaly_interval_sec)
        
        self.clear()
        self.home()
        self.write("Last updated:")
        self.setCursor(1, 0)
        self.write(metrics.datetime)
        time.sleep(self.dispaly_interval_sec)

        self.clear()
        self.home()
        self.write(f"Uptime: {uptime}")
        time.sleep(self.dispaly_interval_sec)
        
        