from datetime import datetime
from enum import Enum
import logging


class SoilMoistureLevel(Enum):
    DRY = "dry"
    MOIST = "moist" 
    WET = "wet"
    
    def __str__(self):
        return self.value
    
class SoilMoisture:
    
    def __init__(self, sensor_value: int):
        self.sensor_value = sensor_value

        if 0 <= sensor_value and sensor_value < 300:
            self.moisture_level = SoilMoistureLevel.DRY
        elif 400 <= sensor_value and sensor_value < 1000:
            self.moisture_level= SoilMoistureLevel.MOIST
        else:
            self.moisture_level = SoilMoistureLevel.WET
    
    @property
    def getSoilMoisture(self):
        logging.info(f"Current moisture: ")
        