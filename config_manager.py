from datetime import datetime
import logging
import os
from time import time
from typing import Optional

from models import GreenhouseAppConfig
from sensors_and_measures.moisture_sensor import SoilMoistureSensor
from sensors_and_measures.tempearature_and_humidity_sensor import TemperatureHumiditySensor
from sensors_and_measures.lcd_display import LcdDisplay
from controllers.greenhouse_controllers import WaterPumpController, WaterAtomizerController
from greenhouse import GreenhouseService

CONFIG_DIRECTORY_NAME = "config"
CONFIG_OVERRIDES_FILE_HEADER = "#AUTOMATICALLY GENERATED FILE - DO NOT EDIT"
CONFIG_OVERRIDES_FILE_NAME = "app_config_overrides.ini"

class GreenhouseConfigManager:
   
   
    def __init__(self):
        self.soil_moisture_sensor: Optional[SoilMoistureSensor] = None
        self.temp_humid_sensor: Optional[TemperatureHumiditySensor] = None
        self.lcd_display: Optional[LcdDisplay] = None
        self.water_pump_controller: Optional[WaterPumpController] = None
        self.atomizing_controller: Optional[WaterAtomizerController] = None
        self.greenhouse_service: Optional[GreenhouseService] = None
        logging.info("GreenhouseConfigManager initialized")
    
    
    def register_components(self, 
                          soil_moisture_sensor: SoilMoistureSensor = None,
                          temp_humid_sensor: TemperatureHumiditySensor = None,
                          lcd_display: LcdDisplay = None,
                          water_pump_controller: WaterPumpController = None,
                          atomizing_controller: WaterAtomizerController = None,
                          greenhouse_service: GreenhouseService = None):

        self.soil_moisture_sensor = soil_moisture_sensor
        self.temp_humid_sensor = temp_humid_sensor
        self.lcd_display = lcd_display
        self.water_pump_controller = water_pump_controller
        self.atomizing_controller = atomizing_controller
        self.greenhouse_service = greenhouse_service
        logging.info("Greenhouse components registered with ConfigManager")
    
    
    def on_config_updated(self, config: GreenhouseAppConfig):
      
        logging.info("Processing configuration update...")
        
        if self.soil_moisture_sensor:
            try:
                self.soil_moisture_sensor.update_thresholds(
                    config.soil_moisture_high,
                    config.soil_moisture_lo
                )
            except Exception as e:
                logging.error(f"Failed to update soil moisture sensor: {e}")
        
        if self.temp_humid_sensor:
            try:
                self.temp_humid_sensor.update_thresholds(
                    config.temperature_high,
                    config.temperature_lo,
                    config.humidity_high,
                    config.humidity_lo
                )
            except Exception as e:
                logging.error(f"Failed to update temperature/humidity sensor: {e}")
        
        if self.lcd_display:
            try:
                self.lcd_display.update_display_settings(
                    config.display_interval_sec,
                    config.display_backlight_on
                )
            except Exception as e:
                logging.error(f"Failed to update LCD display: {e}")
        
        if self.water_pump_controller:
            try:
                self.water_pump_controller.update_watering_duration(
                    config.watering_duration_sec
                )
            except Exception as e:
                logging.error(f"Failed to update water pump controller: {e}")
        
        if self.greenhouse_service:
            try:
                self.greenhouse_service.update_intervals(
                    config.metric_read_sec,
                    config.telemetry_send_sec
                )
            except Exception as e:
                logging.error(f"Failed to update greenhouse service intervals: {e}")
        logging.info("Configuration update propagation completed")
        self._save_config_overrides(config)
        self.greenhouse_service.iot_hub_client.update_twin_properties(config.to_twin_properties_dict())
    
    
    def _save_config_overrides(self, config: GreenhouseAppConfig):
        override_file = os.path.join(os.path.dirname(__file__), CONFIG_DIRECTORY_NAME, CONFIG_OVERRIDES_FILE_NAME)
        if not os.path.exists(os.path.dirname(override_file)):
            os.makedirs(os.path.dirname(override_file), exist_ok=True)
        
        try:
            with open(override_file, 'w') as f:
                f.write(f"{CONFIG_OVERRIDES_FILE_HEADER}\n")
                f.write(f"#Last updated time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("[thresholds]\n")
                f.write(f"temperature_lo = {config.temperature_lo}\n")
                f.write(f"temperature_high = {config.temperature_high}\n")
                f.write(f"humidity_lo = {config.humidity_lo}\n")
                f.write(f"humidity_high = {config.humidity_high}\n")
                f.write(f"soil_moisture_lo = {config.soil_moisture_lo}\n")
                f.write(f"soil_moisture_high = {config.soil_moisture_high}\n\n")
                
                f.write("[actions]\n")
                f.write(f"watering_duration_sec = {config.watering_duration_sec}\n")
                f.write(f"atomizing_duration_sec = {config.atomizing_duration_sec}\n\n")
                
                f.write("[display]\n")
                f.write(f"backlight_on = {'true' if config.display_backlight_on else 'false'}\n")
                f.write(f"interval_sec = {config.display_interval_sec}\n\n")
                
                f.write("[intervals]\n")
                f.write(f"telemetry_send_sec = {config.telemetry_send_sec}\n")
                f.write(f"metric_read_sec = {config.metric_read_sec}\n")
                f.write(f"alerting_sec = {config.alerting_sec}\n")
            
            logging.info(f"Configuration overrides saved to {override_file}")
        except Exception as e:
            logging.error(f"Failed to save configuration overrides: {e}")
            logging.warning("Removing incomplete override file if exists")
            if os.path.exists(override_file):
               os.remove(override_file)
