import logging.config
import sys

from dependency_injector import containers, providers

from greenhouse import GreenhouseService
from sensors_and_measures.moisture_sensor import SoilMoistureSensor
from sensors_and_measures.tempearature_and_humidity_sensor import TemperatureHumiditySensor


class Container(containers.DeclarativeContainer):
    
    config = providers.Configuration(ini_files=["config.ini"])
    
    logging = providers.Resource(
            logging.config.fileConfig,
            fname="logging.ini",
    )
    
    soil_moisture_sensor = providers.Singleton(
        SoilMoistureSensor,
        config.sensors.soil_moisture_sensor_pin.as_int(), 
        )
    
    temp_and_humidity_sensor = providers.Singleton(
        TemperatureHumiditySensor,
        config.sensors.dht_sensor_type,
        config.sensors.temperature_humidity_sensor_pin.as_int()
    )
    
    greenhouse_service = providers.Singleton(
        GreenhouseService,
        soil_moisture_sensor,
        temp_and_humidity_sensor
    )