from enum import Enum
import logging
import time
import seeed_dht

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
        
        if 0 <= humidity and humidity < 45:
            self.humidity_level  = AirHumidityLevel.LO
        elif 45 <= humidity and humidity < 60:
            self.humidity_level = AirHumidityLevel.OPTIMAL
        else:
            self.humidity_level = AirHumidityLevel.HIGH

 
class AirTemperature:
    
    def __init__(self, temperature: float):
        self.temperature = temperature
        
        if 0 <= temperature and temperature < 18:
            self.temperature_level  = AirTemperatureLevel.LO
        elif 18 <= temperature and temperature < 23:
            self.temperature_level = AirTemperatureLevel.OPTIMAL
        else:
            self.temperature_level = AirTemperatureLevel.HIGH
               

class TemperatureHumiditySensor:
    
    def __init__(self, dht_sensor_type: str, pin: str):
        self.sensor = seeed_dht.DHT(dht_sensor_type, pin)
    
    def get_humidity(self):
        logging.info("Detecting humidity...")
        humidity, _ = self.sensor.read()
        return AirHumidity(humidity)
    
    def get_temperature(self):
        logging.info("Detecting temperature...")
        _, temperature = self.sensor.read()
        return AirTemperature(temperature)