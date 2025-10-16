from enum import Enum
import logging
from grove.adc import ADC

from sensors_and_measures.sensor_interface import AlertState, SensorInterface

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
        self.alert_state = AlertState.OK if soil_moisture_level != SoilMoistureLevel.DRY else AlertState.ALERTING

    
    @property
    def getSoilMoisture(self):
        logging.info(f"Current soil moisture: {self.soil_moisture} ")


class SoilMoistureSensor(SensorInterface):
    def __init__(self, pin: int, soil_moisture_threshold_high: int, soil_moisture_threshold_lo: int):
        super().__init__()
        self.channel = pin
        self.soil_moisture_threshold_high = soil_moisture_threshold_high
        self.soil_moisture_threshold_lo = soil_moisture_threshold_lo
        self.adc = ADC()
        
        self._setup_threshold_config()
    
    def _setup_threshold_config(self):
        from alerts import ThresholdConfig, AlertSeverity
        
        self.moisture_threshold_config = ThresholdConfig(
            low_threshold=float(self.soil_moisture_threshold_lo),
            high_threshold=float(self.soil_moisture_threshold_high),
            low_severity=AlertSeverity.HIGH,  
            high_severity=AlertSeverity.MEDIUM,  
            cooldown_seconds=600,  
            enabled=True
        )
    
    def update_thresholds(self, soil_moisture_threshold_high: int, soil_moisture_threshold_lo: int):
        self.soil_moisture_threshold_high = soil_moisture_threshold_high
        self.soil_moisture_threshold_lo = soil_moisture_threshold_lo
        
        self._setup_threshold_config()
        
        logging.info(f"Updated soil moisture thresholds: high={soil_moisture_threshold_high}, lo={soil_moisture_threshold_lo}")


    def get_measurements(self):
        try:
            logging.info("Detecting moisture...")
            value = self.adc.read_voltage(self.channel)
            if value is None or value < 0:
                raise ValueError("Invalid soil moisture reading")
            
            soil_moisture_level = None
            soil_moisture = value / 40
            if 0 <= soil_moisture and soil_moisture < self.soil_moisture_threshold_lo:
                soil_moisture_level = SoilMoistureLevel.DRY
            elif self.soil_moisture_threshold_lo <= soil_moisture and soil_moisture < self.soil_moisture_threshold_high:
                soil_moisture_level = SoilMoistureLevel.MOIST
            else:
                soil_moisture_level = SoilMoistureLevel.WET

            soil_moisture_obj = SoilMoisture(soil_moisture, soil_moisture_level)
            
            self.set_threshold_config(self.moisture_threshold_config)
            self.check_thresholds(soil_moisture_obj.soil_moisture, "soil_moisture")
            
            return soil_moisture_obj
            
        except Exception as e:
            logging.error(f"Error reading soil moisture sensor: {e}")
            self.trigger_sensor_error_alert(str(e))
            return None
    
    def alert(self) -> AlertState:
        return AlertState.OK
