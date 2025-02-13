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
    def __init__(self, soil_moisture: int):
        self.soil_moisture = soil_moisture / 40

        if 0 <= soil_moisture and soil_moisture < 30:
            self.moisture_level = SoilMoistureLevel.DRY
        elif 31 <= soil_moisture and soil_moisture < 50:
            self.moisture_level= SoilMoistureLevel.MOIST
        else:
            self.moisture_level = SoilMoistureLevel.WET
    
    @property
    def getSoilMoisture(self):
        logging.info(f"Current soil moisture: {self.soil_moisture} ")
        
class SoilMoistureSensor(SensorInterface):
    def __init__(self, pin: int):
        self.channel = pin
        self.adc = ADC()

    def get_measurements(self):
        logging.info("Detecting moisture...")
        value = self.adc.read_voltage(self.channel)
        return SoilMoisture(value)
    