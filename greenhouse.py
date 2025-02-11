
import logging
import time

from alive_progress import alive_bar
from datetime import datetime
from azure_services import AzureCosmosDbClient
from models import Greenhouse
import azure.cosmos.exceptions as exceptions
from sensors_and_measures.moisture_sensor import SoilMoistureSensor
from sensors_and_measures.tempearature_and_humidity_sensor import TemperatureHumiditySensor


class GreenhouseService:
    def __init__(
        self, 
        soil_moisture_sensor: SoilMoistureSensor,
        temp_humid_sensor: TemperatureHumiditySensor,
        db_client: AzureCosmosDbClient 
        ):
        
        self.soil_moisture_sensor = soil_moisture_sensor
        self.temp_humid_sensor = temp_humid_sensor
        self.db_client = db_client


    def start_measuring(self, interval_in_minutes: int = 15):
        logging.info('saving current measures to db')
        self._save_measurement()
        logging.info('waiting for {0} minutes until next measure'.format(interval_in_minutes))
            
            
    def _save_measurement(self):
        metrics = self._measure()  
        try:
            result = self.db_client.insert_measure(measure=metrics)        
        except exceptions.CosmosHttpResponseError as e:
            logging.error('save_measurement has caught an error. {0}'.format(e.message))
        logging.info('measures saved in database with id: {0}'.format(result["id"]))
      
                           
    def _measure(self) -> Greenhouse:
        logging.info("Measuring...")

        soil_moisture = self.soil_moisture_sensor.get_soil_moisture()
        air_temp = self.temp_humid_sensor.get_temperature()
        air_humid = self.temp_humid_sensor.get_humidity()
        greenhouse_metrics = Greenhouse(
            soil_moisture=soil_moisture,
            air_temperature=air_temp,
            air_humidity=air_humid
            )
        logging.info(greenhouse_metrics.to_cosmos_db_item)
        return greenhouse_metrics
    