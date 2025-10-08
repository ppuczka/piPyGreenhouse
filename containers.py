import logging.config
import os
import sys

from dependency_injector import containers, providers
from dotenv import load_dotenv

from azure_services import AzureCosmosDbClient, AzureIotHubClient, AzureIotHubIncomingSignalHandler
from greenhouse import GreenhouseService
from controllers.greenhouse_controllers import WaterPumpController
from models import GreenhouseAppConfig
from sensors_and_measures.lcd_display import LcdDisplay
from sensors_and_measures.light_sensor import LightIntensitySensor
from sensors_and_measures.moisture_sensor import SoilMoistureSensor
from sensors_and_measures.tempearature_and_humidity_sensor import TemperatureHumiditySensor


class Container(containers.DeclarativeContainer):
    load_dotenv(os.path.join(os.path.dirname(__file__),'.env'))

    config_file = os.path.join(os.path.dirname(__file__), "config.ini")
    app_defaults_file = os.path.join(os.path.dirname(__file__), "app_defaults.ini")

    config = providers.Configuration()
    config.from_ini(config_file)
    config.azure.iot.hub.connection.string.from_env("AZURE_IOT_HUB_CONNECTION_STRING", required=True)

    greenhouse_app_defaults = providers.Configuration()
    greenhouse_app_defaults.from_ini(app_defaults_file) 

    greenhouse_app_config = providers.Singleton(
        GreenhouseAppConfig,
        greenhouse_app_defaults.thresholds.temperature_lo.as_int(),
        greenhouse_app_defaults.thresholds.temperature_high.as_int(),
        greenhouse_app_defaults.thresholds.humidity_lo.as_int(),
        greenhouse_app_defaults.thresholds.humidity_high.as_int(),
        greenhouse_app_defaults.thresholds.soil_moisture_lo.as_int(),
        greenhouse_app_defaults.thresholds.soil_moisture_high.as_int(),
        greenhouse_app_defaults.actions.watering_duration_sec.as_int(),
        greenhouse_app_defaults.actions.atomizing_duration_sec.as_int(),
        greenhouse_app_defaults.display.backlight_on.as_(lambda x: x.lower() in ('true', '1', 'yes', 'on')),
        greenhouse_app_defaults.display.interval_sec.as_int(),
        greenhouse_app_defaults.intervals.telemetry_send_sec.as_int(),
        greenhouse_app_defaults.intervals.metric_read_sec.as_int(),
        greenhouse_app_defaults.intervals.alerting_sec.as_int()
    )
    
    
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
    
    
    water_pump_controller = providers.Singleton(
        WaterPumpController,
        config.controllers.water_pump_controller_pin.as_int(),
        greenhouse_app_config.provided.watering_duration_sec
        )
    
    
    iot_hub_signal_handler = providers.Singleton(
        AzureIotHubIncomingSignalHandler,
        water_pump_controller
    )
    
    
    iot_hub_client = providers.Singleton(
        AzureIotHubClient,
        iot_hub_signal_handler,
        config.azure.iot.hub.connection.string
    )


    soil_moisture_sensor = providers.Singleton(
        SoilMoistureSensor,
        config.sensors.soil_moisture_sensor_pin.as_int(), 
        greenhouse_app_config.provided.soil_moisture_high,
        greenhouse_app_config.provided.soil_moisture_lo
    )
    
    
    temp_and_humidity_sensor = providers.Singleton(
        TemperatureHumiditySensor,
        config.sensors.dht_sensor_type,
        config.sensors.temperature_humidity_sensor_pin.as_int(),
        greenhouse_app_config.provided.temperature_high,
        greenhouse_app_config.provided.temperature_lo,
        greenhouse_app_config.provided.humidity_high,
        greenhouse_app_config.provided.humidity_lo
    )
    
    
    light_intensity_sensor = providers.Singleton(
        LightIntensitySensor,
        config.sensors.light_intensity_sensor_pin.as_int()
    )
    
    
    lcd_display = providers.Singleton(
        LcdDisplay,
        greenhouse_app_config.provided.display_interval_sec,
        greenhouse_app_config.provided.display_backlight_on
    )
    

    greenhouse_service = providers.Singleton(
        GreenhouseService,
        soil_moisture_sensor,
        temp_and_humidity_sensor,
        light_intensity_sensor,
        lcd_display,
        database_client,
        iot_hub_client,
        greenhouse_app_config.provided.metric_read_sec,
        greenhouse_app_config.provided.telemetry_send_sec
    )