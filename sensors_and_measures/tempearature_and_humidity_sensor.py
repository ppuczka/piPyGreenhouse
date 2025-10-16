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
    def __init__(self, humidity: float, humidity_level: AirHumidityLevel = None):
        self.humidity = humidity
        if humidity_level is None:
            # Default level calculation if not provided
            if 0 <= humidity and humidity < 45:
                self.humidity_level = AirHumidityLevel.LO
            elif 45 <= humidity and humidity < 60:
                self.humidity_level = AirHumidityLevel.OPTIMAL
            else:
                self.humidity_level = AirHumidityLevel.HIGH
        else:
            self.humidity_level = humidity_level

 
class AirTemperature:
    def __init__(self, temperature: float, temperature_level: AirTemperatureLevel = None):
        self.temperature = temperature
        if temperature_level is None:
            # Default level calculation if not provided
            if 0 <= temperature and temperature < 18:
                self.temperature_level = AirTemperatureLevel.LO
            elif 18 <= temperature and temperature < 23:
                self.temperature_level = AirTemperatureLevel.OPTIMAL
            else:
                self.temperature_level = AirTemperatureLevel.HIGH
        else:
            self.temperature_level = temperature_level


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
        super().__init__()
        self.sensor = seeed_dht.DHT(dht_sensor_type, pin)
        self.temp_threshold_high = temp_threshold_high
        self.temp_threshold_lo = temp_threshold_lo
        self.humid_threshold_high = humid_threshold_high
        self.humid_threshold_lo = humid_threshold_lo
        
        self._setup_threshold_configs()
    
    def _setup_threshold_configs(self):
        from alerts import ThresholdConfig, AlertSeverity
        
        self.temp_threshold_config = ThresholdConfig(
            low_threshold=float(self.temp_threshold_lo),
            high_threshold=float(self.temp_threshold_high),
            low_severity=AlertSeverity.MEDIUM,
            high_severity=AlertSeverity.HIGH,
            cooldown_seconds=300,  # 5 minutes
            enabled=True
        )
        
        self.humid_threshold_config = ThresholdConfig(
            low_threshold=float(self.humid_threshold_lo),
            high_threshold=float(self.humid_threshold_high),
            low_severity=AlertSeverity.MEDIUM,
            high_severity=AlertSeverity.MEDIUM,
            cooldown_seconds=300,  # 5 minutes
            enabled=True
        )

    def update_thresholds(self, temp_threshold_high: int, temp_threshold_lo: int, 
                         humid_threshold_high: int, humid_threshold_lo: int):
        self.temp_threshold_high = temp_threshold_high
        self.temp_threshold_lo = temp_threshold_lo
        self.humid_threshold_high = humid_threshold_high
        self.humid_threshold_lo = humid_threshold_lo
        
        self._setup_threshold_configs()
        
        logging.info(f"Updated temperature thresholds: high={temp_threshold_high}, lo={temp_threshold_lo}")
        logging.info(f"Updated humidity thresholds: high={humid_threshold_high}, lo={humid_threshold_lo}")
    
    def get_measurements(self):
        try:
            humidity_obj, temperature_obj = self._get_humidity(), self._get_temperature()
            
            if humidity_obj and temperature_obj:
                self.set_threshold_config(self.humid_threshold_config)
                self.check_thresholds(humidity_obj.humidity, "humidity")
                
                self.set_threshold_config(self.temp_threshold_config)
                self.check_thresholds(temperature_obj.temperature, "temperature")
            
            return humidity_obj, temperature_obj
            
        except Exception as e:
            logging.error(f"Error reading temperature/humidity sensor: {e}")
            self.trigger_sensor_error_alert(str(e))
            return None, None
    
    def _get_humidity(self):
        try:
            logging.info("Detecting humidity...")
            humidity, _ = self.sensor.read()
            if humidity is None or humidity < 0:
                raise ValueError("Invalid humidity reading")
                
            humidity_level = None
            if 0 <= humidity and humidity < self.humid_threshold_lo:
                humidity_level = AirHumidityLevel.LO
            elif self.humid_threshold_lo <= humidity and humidity < self.humid_threshold_high:
                humidity_level = AirHumidityLevel.OPTIMAL
            else:
                humidity_level = AirHumidityLevel.HIGH
            return AirHumidity(humidity, humidity_level)
        except Exception as e:
            logging.error(f"Failed to read humidity: {e}")
            return None

    def _get_temperature(self):
        try:
            logging.info("Detecting temperature...")
            _, temperature = self.sensor.read()
            if temperature is None:
                raise ValueError("Invalid temperature reading")
                
            temperature_level = None
            if 0 <= temperature and temperature < self.temp_threshold_lo:
                temperature_level = AirTemperatureLevel.LO
            elif self.temp_threshold_lo <= temperature and temperature < self.temp_threshold_high:
                temperature_level = AirTemperatureLevel.OPTIMAL
            else:
                temperature_level = AirTemperatureLevel.HIGH
            return AirTemperature(temperature, temperature_level)
        except Exception as e:
            logging.error(f"Failed to read temperature: {e}")
            return None