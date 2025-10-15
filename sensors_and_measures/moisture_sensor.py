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
    def __init__(self, soil_moisture: int, soil_moisture_level: SoilMoistureLevel = None):
        self.soil_moisture = soil_moisture
        self.soil_moisture_level = soil_moisture_level

    @property
    def getSoilMoisture(self):
        logging.info(f"Current soil moisture: {self.soil_moisture} ")
    
        
class SoilMoistureSensor(SensorInterface):
    def __init__(self, pin: int, soil_moisture_threshold_high: int, soil_moisture_threshold_lo: int):
        self.channel = pin
        self.soil_moisture_threshold_high = soil_moisture_threshold_high
        self.soil_moisture_threshold_lo = soil_moisture_threshold_lo
        self.adc = ADC()
    
    def update_thresholds(self, soil_moisture_threshold_high: int, soil_moisture_threshold_lo: int):
        self.soil_moisture_threshold_high = soil_moisture_threshold_high
        self.soil_moisture_threshold_lo = soil_moisture_threshold_lo
        logging.info(f"Updated soil moisture thresholds: high={soil_moisture_threshold_high}, lo={soil_moisture_threshold_lo}")


    def get_measurements(self):
        logging.info("Detecting moisture...")
        value = self.adc.read_voltage(self.channel)
        
        soil_moisture_level = None
        soil_moisture = value / 40
        if 0 <= soil_moisture and soil_moisture < self.soil_moisture_threshold_lo:
            soil_moisture_level = SoilMoistureLevel.DRY
        elif self.soil_moisture_threshold_lo <= soil_moisture and soil_moisture < self.soil_moisture_threshold_high:
            soil_moisture_level = SoilMoistureLevel.MOIST
        else:
            soil_moisture_level = SoilMoistureLevel.WET

        return SoilMoisture(soil_moisture, soil_moisture_level)


    def alert(self):
        logging.info("Soil moisture alert!")