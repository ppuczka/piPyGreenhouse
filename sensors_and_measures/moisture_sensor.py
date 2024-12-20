import logging
from grove.adc import ADC
from .soil_moisture import SoilMoisture

__all__ = ["SoilMoistureSensor"]


class SoilMoistureSensor:
    def __init__(self, pin: int):
        self.channel = pin
        self.adc = ADC()


    @property
    def moisture(self):
        value = self.adc.read_voltage(self.channel)
        return value
     

    def get_soil_moisture(self):
        logging.info("Detecting moisture...")
        return SoilMoisture(self.moisture)
    