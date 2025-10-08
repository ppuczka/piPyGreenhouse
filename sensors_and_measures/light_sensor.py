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
    
    # Todo: implement alert logic based on thresholds
    def alert(self):
        logging.info("Light intensity alert!")
        
    # Todo: implement proper lux calculation based on sensor datasheet
    def _calculate_lux(self, raw_value: int) -> float:
        # Example conversion formula (this may vary based on the sensor)
        return (raw_value / 1023.0) * 1000  # Convert to lux assuming a max of 1000 lux
    
    # Todo: implement proper lux calculation based on sensor datasheet
    def _calculate_daily_light_integral(self, lux_values: list, time_interval_hours: float) -> float:
        # DLI = (Sum of lux readings) * (time interval in hours) / 1000000
        return (sum(lux_values) * time_interval_hours) / 1000000