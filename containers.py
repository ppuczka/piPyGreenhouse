import logging.config
import os
import sys

from dependency_injector import containers, providers
from dotenv import load_dotenv

from azure_services import AzureCosmosDbClient, AzureIotHubClient
from greenhouse import GreenhouseService
from sensors_and_measures.lcd_display import LcdDisplay
from sensors_and_measures.light_sensor import LightIntensitySensor
from sensors_and_measures.moisture_sensor import SoilMoistureSensor
from sensors_and_measures.tempearature_and_humidity_sensor import TemperatureHumiditySensor


class Container(containers.DeclarativeContainer):
    load_dotenv(os.path.join(os.path.dirname(__file__),'.env'))

    config_file = os.path.join(os.path.dirname(__file__), "config.ini")

    config = providers.Configuration()
    config.from_ini(config_file)
    config.azure.iot.hub.connection.string.from_env("AZURE_IOT_HUB_CONNECTION_STRING", required=True)
       
    logging = providers.Resource(
            logging.config.fileConfig,
            fname=os.path.join(os.path.dirname(__file__), "logging.ini"),
    )
  
    database_client = providers.Singleton(
        AzureCosmosDbClient,
        config.database.uri,
        config.database.name,
        config.database.container_name
    )
    
    iot_hub_client = providers.Singleton(
        AzureIotHubClient,
        config.azure.iot.hub.connection.string
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
    
    light_intensity_sensor = providers.Singleton(
        LightIntensitySensor,
        config.sensors.light_intensity_sensor_pin.as_int()
    )
    
    lcd_display = providers.Singleton(
        LcdDisplay 
    )
    
    greenhouse_service = providers.Singleton(
        GreenhouseService,
        soil_moisture_sensor,
        temp_and_humidity_sensor,
        light_intensity_sensor,
        lcd_display,
        database_client,
        iot_hub_client
    )