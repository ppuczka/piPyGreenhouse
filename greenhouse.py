import asyncio
import json
import logging
import threading
import time

from azure_services import AzureCosmosDbClient, AzureIotHubClient, AzureIotHubClientException, AzureIotHubMessage, AzureIotHubSignalType
from models import Greenhouse, GreenhouseAppConfig
import azure.cosmos as exceptions
from sensors_and_measures.lcd_display import LcdDisplay
from sensors_and_measures.light_sensor import LightIntensitySensor
from sensors_and_measures.moisture_sensor import SoilMoistureSensor
from sensors_and_measures.tempearature_and_humidity_sensor import TemperatureHumiditySensor


class GreenhouseService:
    def __init__(
        self, 
        soil_moisture_sensor: SoilMoistureSensor,
        temp_humid_sensor: TemperatureHumiditySensor,
        light_intensity_sensor: LightIntensitySensor,
        lcd_display: LcdDisplay,
        db_client: AzureCosmosDbClient,
        iot_hub_client: AzureIotHubClient,
        app_config: GreenhouseAppConfig,
        config_manager=None,
        alert_observer=None
        ):
        
        self.soil_moisture_sensor = soil_moisture_sensor
        self.temp_humid_sensor = temp_humid_sensor
        self.light_intensity_sensor = light_intensity_sensor
        self.lcd_display = lcd_display
        self.db_client = db_client
        self.iot_hub_client = iot_hub_client
        self.start_time = time.time()
        self.app_config = app_config

        self.measure_interval_sec = app_config.metric_read_sec
        self.save_interval_min = app_config.telemetry_send_sec / 60 

        self.greenhouse_metrics  = None
        self.lock = threading.Lock()
        
        if config_manager is not None:
            self._setup_config_manager(config_manager)
            
        if alert_observer is not None:
            self._setup_alert_observer(alert_observer)

    
    async def run_in_parallel(self):
        try:
            self.iot_hub_client.connect()
        except AzureIotHubClientException as iotEx:
            logging.error(f"Failed to connect to IoT Hub: {iotEx}")
            return
        except Exception as ex:
            logging.error(f"Unexpected error while connecting to IoT Hub: {ex}")

        self.iot_hub_client.update_twin_properties(self.app_config.to_twin_properties_dict())

        measure_thread = threading.Thread(
            target=self._start_measuring_loop,
            args=(self.measure_interval_sec, self.save_interval_min),
            daemon=True
        )
        
        display_thread = threading.Thread(target=self._display_measures, daemon=True)
        
                
        measure_thread.start()
        measure_thread.join()

        # display_thread.start()
        # display_thread.join()
  

    def update_intervals(self, metric_read_sec: int, telemetry_send_sec: int):
        with self.lock:
            old_measure_interval = self.measure_interval_sec
            old_save_interval = self.save_interval_min
            
            self.measure_interval_sec = metric_read_sec
            self.save_interval_min = telemetry_send_sec / 60
            
            logging.info(f"Updated measurement interval: {old_measure_interval} -> {metric_read_sec} seconds")
            logging.info(f"Updated telemetry interval: {old_save_interval:.1f} -> {self.save_interval_min:.1f} minutes")


    def _setup_config_manager(self, config_manager):
        water_pump_controller = None
        atomizing_controller = None
        
        if hasattr(self.iot_hub_client, 'signal_handler') and hasattr(self.iot_hub_client.signal_handler, 'greenhouse_controller_registry'):
            registry = self.iot_hub_client.signal_handler.greenhouse_controller_registry
            water_pump_controller = registry.get_controller("pump")
            atomizing_controller = registry.get_controller("atomizer")
        
        config_manager.register_components(
            soil_moisture_sensor=self.soil_moisture_sensor,
            temp_humid_sensor=self.temp_humid_sensor,
            lcd_display=self.lcd_display,
            water_pump_controller=water_pump_controller,
            atomizing_controller=atomizing_controller,
            greenhouse_service=self
        )
        
        self.app_config.register_update_callback(config_manager.on_config_updated)
        
        logging.info("Configuration manager setup completed")

    def _setup_alert_observer(self, alert_observer):
        try:
            alert_observer.set_iot_hub_client(self.iot_hub_client)
            logging.info("Alert observer configured with IoT Hub client")
        except Exception as e:
            logging.error(f"Failed to setup alert observer: {e}")


    def _start_measuring_loop(self, measure_interval_sec: int, save_interval_min: int):
        last_save_time = time.time()
        while True:
            logging.info("Performing measurement...")
            with self.lock:
                self._measure()
                # Save only if 15 minutes have passed
                time_since_last_save = time.time() - last_save_time
                if time_since_last_save >= save_interval_min * 60:
                # if True:
                    self._send_metrics_telemetry_to_iot_hub()
                    # self._save_measurement()
                    last_save_time = time.time()
                else:
                    minutes, seconds = divmod(int(time_since_last_save), 60)
                    logging.info(f"Skipping save, not enough time has passed since last save: {minutes:02}:{seconds:02} (MM:SS)")
            time.sleep(measure_interval_sec)


    def _display_measures(self):
        self.lcd_display.status()
        logging.info("Runing lcd measurement display...")
        logging.info(f"Begining displaying greenhouse metrics on LCD loop")
        while True: 
            uptime = self._get_uptime()
            with self.lock:  
                if self.greenhouse_metrics is not None:
                    self.lcd_display.display_greenhouse_info(self.greenhouse_metrics, uptime)
            time.sleep(30)
       
        
    def _save_measurement_to_cosmos_db(self):
        try:
            result = self.db_client.insert_measure(measure=self.greenhouse_metrics)        
        except exceptions.CosmosHttpResponseError as e:
            logging.error('save_measurement has caught an error. {0}'.format(e.message))
            return
        logging.info('measures saved in database with id: {0}'.format(result["id"]))
       
                    
    def _measure(self):
        logging.info("Measuring...")
        soil_moisture = self.soil_moisture_sensor.get_measurements()
        air_humid, air_temp = self.temp_humid_sensor.get_measurements()
        light_intensity = self.light_intensity_sensor.get_measurements()
        self.greenhouse_metrics = Greenhouse(
            soil_moisture=soil_moisture,
            air_temperature=air_temp,
            air_humidity=air_humid,
            light_intensity=light_intensity
        )
        logging.info(f"Current metrics read: {json.dumps(self.greenhouse_metrics.to_cosmos_db_item(), indent=2)}")
       
       
    def _send_metrics_telemetry_to_iot_hub(self):
        if self.greenhouse_metrics is not None and self.greenhouse_metrics.get_alerting():
            message = AzureIotHubMessage(
                message_type=AzureIotHubSignalType.ALERT,
                content=self.greenhouse_metrics
            )
            self.iot_hub_client.send_telemetry(message)
            logging.info(f"Telemetry sent: {self.greenhouse_metrics.to_cosmos_db_item()}")
        else:
            logging.warning("No greenhouse metrics available to send as telemetry.")
    
    
    def _update_twins():
        pass
    
            
    def _get_uptime(self) -> str:
        current_time = time.time()
        uptime_seconds = current_time - self.start_time

        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
