from grove.adc import ADC
import logging

from sensors_and_measures.sensor_interface import SensorInterface

class LightIntensity:    
    def __init__(self, intensity: float):
        self.intensity = intensity

    @property
    def getLightIntensity(self):
        logging.info(f"Current light intensity: {self.intensity}")
        
class LightIntensitySensor(SensorInterface):
    def __init__(self, pin: int):
        self.channel = pin
        self.adc = ADC()

    def get_measurements(self):
        logging.info("Detecting light intensity...")
        value = self.adc.read(self.channel)
        return LightIntensity(value)
    