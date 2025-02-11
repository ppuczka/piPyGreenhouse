from enum import Enum
import logging
from grove.adc import ADC

from sensors_and_measures.sensor_interface import SensorInterface

__all__ = ["SoilMoistureSensor"]


class SoilMoistureLevel(Enum):
    DRY = "dry"
    MOIST = "moist" 
    WET = "wet"
    
    def __str__(self):
        return self.value
    
class SoilMoisture:
    def __init__(self, sensor_value: int):
        self.sensor_value = sensor_value / 40

        if 0 <= sensor_value and sensor_value < 30:
            self.moisture_level = SoilMoistureLevel.DRY
        elif 31 <= sensor_value and sensor_value < 50:
            self.moisture_level= SoilMoistureLevel.MOIST
        else:
            self.moisture_level = SoilMoistureLevel.WET
    
    @property
    def getSoilMoisture(self):
        logging.info(f"Current moisture: ")
        
class SoilMoistureSensor(SensorInterface):
    def __init__(self, pin: int):
        self.channel = pin
        self.adc = ADC()

    def get_measurements(self):
        logging.info("Detecting moisture...")
        value = self.adc.read_voltage(self.channel)
        return SoilMoisture(value)
    