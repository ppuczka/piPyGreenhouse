from dataclasses import dataclass
import logging
import uuid
from datetime import datetime
from sensors_and_measures.light_sensor import LightIntensity
from sensors_and_measures.moisture_sensor import SoilMoisture
from sensors_and_measures.tempearature_and_humidity_sensor import AirHumidity, AirTemperature
import json

class Greenhouse:
    def __init__(self, soil_moisture: SoilMoisture, air_temperature: AirTemperature, air_humidity: AirHumidity, light_intensity: LightIntensity):
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.soil_moisture = soil_moisture
        self.air_temperature = air_temperature
        self.air_humidity = air_humidity
        self.light_intensity = light_intensity
        
        _uuid = uuid.uuid4()
        self.id = _uuid.hex 
     
        
    def to_cosmos_db_item(self): 
        return {
            "id": self.id,
            "temperature": self.air_temperature.temperature,
            "temperature_level": self.air_temperature.temperature_level.value,
            "humidity": self.air_humidity.humidity,
            "humidity_level": self.air_humidity.humidity_level.value,
            "soil_moisture": self.soil_moisture.soil_moisture,
            "soil_moisture_level": self.soil_moisture.moisture_level.value,
            "light_intensity": self.light_intensity.intensity,
            "date_time": self.datetime
            }


    def display_measure(self): return f'''Date & time: {self.datetime}
                        Soil moisture (value: {self.soil_moisture.soil_moisture}, moisture_level: {self.soil_moisture.moisture_level})
                        Air temperature (value: {self.air_temperature.temperature}, temperature_level: {self.air_temperature.temperature_level}) 
                        Air humidity (value: {self.air_humidity.humidity}, humidity_level: {self.air_humidity.humidity_level}),
                        Light intensity (value: {self.light_intensity})'''


@dataclass
class GreenhouseAppConfig:
    temperature_lo: int
    temperature_high: int
    humidity_lo: int
    humidity_high: int
    soil_moisture_lo: int
    soil_moisture_high: int

    watering_duration_sec: int
    atomizing_duration_sec: int

    display_backlight_on: bool
    display_interval_sec: int

    telemetry_send_sec: int
    metric_read_sec: int
    alerting_sec: int

    def __post_init__(self):
        self._update_callbacks = []
    
    def register_update_callback(self, callback):
        """Register a callback that will be called when config is updated"""
        self._update_callbacks.append(callback)
    
    def update_from_twin_patch(self, patch: dict) -> bool:
        """Update configuration from Azure IoT twin patch and notify callbacks"""
        updated = False
        
        # Mapping twin property names to config field names
        field_mapping = {
            'temperature_lo': 'temperature_lo',
            'temperature_high': 'temperature_high',
            'humidity_lo': 'humidity_lo',
            'humidity_high': 'humidity_high',
            'soil_moisture_lo': 'soil_moisture_lo',
            'soil_moisture_high': 'soil_moisture_high',
            'watering_duration_sec': 'watering_duration_sec',
            'atomizing_duration_sec': 'atomizing_duration_sec',
            'display_backlight_on': 'display_backlight_on',
            'display_interval_sec': 'display_interval_sec',
            'telemetry_send_sec': 'telemetry_send_sec',
            'metric_read_sec': 'metric_read_sec',
            'alerting_sec': 'alerting_sec'
        }
        
        for twin_property, field_name in field_mapping.items():
            if twin_property in patch:
                old_value = getattr(self, field_name)
                new_value = patch[twin_property]
                
                # Validate and convert types
                try:
                    if field_name == 'display_backlight_on':
                        new_value = bool(new_value)
                    else:
                        new_value = int(new_value)
                        
                    setattr(self, field_name, new_value)
                    updated = True
                    logging.info(f"Updated config {field_name}: {old_value} -> {new_value}")
                except (ValueError, TypeError) as e:
                    logging.warning(f"Failed to update config {field_name}: {e}")
        
        if updated:
            # Notify all registered callbacks
            for callback in self._update_callbacks:
                try:
                    callback(self)
                except Exception as e:
                    logging.error(f"Error in config update callback: {e}")
                    
        return updated
    
    def to_dict(self):
        return self.__dict__.copy()
    
    
    def to_json(self):
        data = self.__dict__.copy()
        # Remove callbacks from the dict as they're not serializable
        data.pop('_update_callbacks', None)
        if data is not None:
            data["report_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return json.dumps(data)
        logging.error("Failed to convert to JSON")
        return "{}"