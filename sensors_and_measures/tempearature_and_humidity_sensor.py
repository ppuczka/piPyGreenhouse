from enum import Enum
import logging
import time
import seeed_dht

from sensors_and_measures.sensor_interface import SensorInterface

__all__ = ["TemperatureHumiditySensor"]


class AirHumidityLevel(Enum):
    HIGH = "high"
    OPTIMAL = "optimal" 
    LO = "lo"
    
    def __str__(self):
        return self.value


class AirTemperatureLevel(Enum):
    HIGH = "high"
    OPTIMAL = "optimal" 
    LO = "lo"
    
    def __str__(self):
        return self.value

    
class AirHumidity:    
    def __init__(self, humidity: float):
        self.humidity = humidity
        
        if 0 <= humidity and humidity < self.humid_threshold_lo:
            self.humidity_level  = AirHumidityLevel.LO
        elif self.humid_threshold_lo <= humidity and humidity < self.humid_threshold_high:
            self.humidity_level = AirHumidityLevel.OPTIMAL
        else:
            self.humidity_level = AirHumidityLevel.HIGH

 
class AirTemperature:
    def __init__(self, temperature: float):
        self.temperature = temperature

        if 0 <= temperature and temperature < self.temp_threshold_lo:
            self.temperature_level = AirTemperatureLevel.LO
        elif self.temp_threshold_lo <= temperature and temperature < self.temp_threshold_high:
            self.temperature_level = AirTemperatureLevel.OPTIMAL
        else:
            self.temperature_level = AirTemperatureLevel.HIGH
               

class TemperatureHumiditySensor(SensorInterface):
    def __init__(
        self,
        dht_sensor_type: str,
        pin: str,
        temp_threshold_high: int,
        temp_threshold_lo: int,
        humid_threshold_high: int,
        humid_threshold_lo: int
        ):
        self.sensor = seeed_dht.DHT(dht_sensor_type, pin)
        self.temp_threshold_high = temp_threshold_high
        self.temp_threshold_lo = temp_threshold_lo
        self.humid_threshold_high = humid_threshold_high
        self.humid_threshold_lo = humid_threshold_lo
    
    def update_thresholds(self, temp_threshold_high: int, temp_threshold_lo: int, 
                         humid_threshold_high: int, humid_threshold_lo: int):
        """Update the sensor thresholds dynamically"""
        self.temp_threshold_high = temp_threshold_high
        self.temp_threshold_lo = temp_threshold_lo
        self.humid_threshold_high = humid_threshold_high
        self.humid_threshold_lo = humid_threshold_lo
        logging.info(f"Updated temperature thresholds: high={temp_threshold_high}, lo={temp_threshold_lo}")
        logging.info(f"Updated humidity thresholds: high={humid_threshold_high}, lo={humid_threshold_lo}")
    
    def get_measurements(self):
        return self._get_humidity(), self._get_temperature()
    
    def _get_humidity(self):
        logging.info("Detecting humidity...")
        humidity, _ = self.sensor.read()
        return AirHumidity(humidity)
    
    def _get_temperature(self):
        logging.info("Detecting temperature...")
        _, temperature = self.sensor.read()
        return AirTemperature(temperature)