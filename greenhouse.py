
import logging
import threading
import time

from azure_services import AzureCosmosDbClient
from models import Greenhouse
import azure.cosmos.exceptions as exceptions
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
        ):
        
        self.soil_moisture_sensor = soil_moisture_sensor
        self.temp_humid_sensor = temp_humid_sensor
        self.light_intensity_sensor = light_intensity_sensor
        self.lcd_display = lcd_display
        self.db_client = db_client
        self.start_time = time.time()
        
        self.greenhouse_metrics  = None
        self.lock = threading.Lock()

    def run_in_parallel(self, interval_in_minutes: int = 15):
        measure_thread = threading.Thread(target=self._start_measuring_loop, args=(interval_in_minutes,), daemon=True)
        display_thread = threading.Thread(target=self._display_measures, daemon=True)

        # measure_thread.start()
        display_thread.start()

        # measure_thread.join()
        display_thread.join()

    def _start_measuring_loop(self, interval_in_minutes: int = 15):
       while True:
            logging.info("Performing measurement...")
            with self.lock:
                self._save_measurement()
            time.sleep(interval_in_minutes * 60)
    
    def _display_measures(self):
        logging.info("Runing lcd measurement display...")
        self.lcd_display.status()
        logging.info("Status")
        while True: 
            uptime = self._get_uptime()
            with self.lock:  
                if self.greenhouse_metrics is not None:
                    self.lcd_display.display_greenhouse_info(self.greenhouse_metrics, uptime)
            time.sleep(30)
        
    def _save_measurement(self):
        self._measure()  
        try:
            result = self.db_client.insert_measure(measure=self.greenhouse_metrics)        
        except exceptions.CosmosHttpResponseError as e:
            logging.error('save_measurement has caught an error. {0}'.format(e.message))
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
        logging.info(self.greenhouse_metrics.to_cosmos_db_item)
       
       
    def _get_uptime(self) -> str:
        current_time = time.time()
        uptime_seconds = current_time - self.start_time

        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"