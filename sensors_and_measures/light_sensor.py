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
    def __init__(self, pin: int, light_threshold_low: float = 100, light_threshold_high: float = 800):
        super().__init__()
        self.channel = pin
        self.adc = ADC()
        self.light_threshold_low = light_threshold_low
        self.light_threshold_high = light_threshold_high
        
        self._setup_threshold_config()
    
    def _setup_threshold_config(self):
        from alerts import ThresholdConfig, AlertSeverity
        
        self.light_threshold_config = ThresholdConfig(
            low_threshold=float(self.light_threshold_low),
            high_threshold=float(self.light_threshold_high),
            low_severity=AlertSeverity.MEDIUM,  
            high_severity=AlertSeverity.LOW,
            cooldown_seconds=900,
            enabled=True
        )

    def get_measurements(self):
        try:
            logging.info("Detecting light intensity...")
            value = self.adc.read(self.channel)
            if value is None or value < 0:
                raise ValueError("Invalid light intensity reading")
                
            light_intensity_obj = LightIntensity(value)
            
            # Check thresholds and trigger alerts
            self.set_threshold_config(self.light_threshold_config)
            self.check_thresholds(light_intensity_obj.intensity, "light_intensity")
            
            return light_intensity_obj
            
        except Exception as e:
            logging.error(f"Error reading light intensity sensor: {e}")
            self.trigger_sensor_error_alert(str(e))
            return None
    
    def alert(self):
        logging.info("Light intensity alert!")
        
    def _calculate_lux(self, raw_value: int) -> float:
        # Example conversion formula (this may vary based on the sensor)
        return (raw_value / 1023.0) * 1000  # Convert to lux assuming a max of 1000 lux
    
    # Todo: implement proper lux calculation based on sensor datasheet
    def _calculate_daily_light_integral(self, lux_values: list, time_interval_hours: float) -> float:
        # DLI = (Sum of lux readings) * (time interval in hours) / 1000000
        return (sum(lux_values) * time_interval_hours) / 1000000