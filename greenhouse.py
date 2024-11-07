
import logging
import time

from datetime import datetime
from sensors_and_measures.moisture_sensor import SoilMoistureSensor
from sensors_and_measures.soil_moisture import SoilMoisture
from sensors_and_measures.tempearature_and_humidity_sensor import AirHumidity, AirTemperature, TemperatureHumiditySensor


class Greenhouse:
    def __init__(
        self,
        soil_moisture: SoilMoisture,
        air_temperature: AirTemperature,
        air_humidity: AirHumidity
    ):
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.soil_moisture = soil_moisture
        self.air_temperature = air_temperature
        self.air_humidity = air_humidity

    def __str__(self): return f'''Date & time: {self.datetime}
                        Soil moisture (value: {self.soil_moisture.sensor_value}, moisture_level: {self.soil_moisture.moisture_level})
                        Air temperature (value: {self.air_temperature.temperature}, temperature_level: {self.air_temperature.temperature_level}) 
                        Air humidity (value: {self.air_humidity.humidity}, humidity_level: {self.air_humidity.humidity_level}) '''

class GreenhouseService:
    def __init__(self, 
                 soil_moisture_sensor: SoilMoistureSensor,
                 temp_humid_sensor: TemperatureHumiditySensor):
        
        self.soil_moisture_sensor = soil_moisture_sensor
        self.temp_humid_sensor = temp_humid_sensor
    
    def measure(self):
        print("Measuring...")
        while True:
            soil_moisture = self.soil_moisture_sensor.get_soil_moisture()
            air_temp = self.temp_humid_sensor.get_temperature()
            air_humid = self.temp_humid_sensor.get_humidity()
            greenhouse_metrics = Greenhouse(
                soil_moisture=soil_moisture,
                air_temperature=air_temp,
                air_humidity=air_humid
                )
            logging.info(greenhouse_metrics)
            time.sleep(1)
            