import uuid
from datetime import datetime
from sensors_and_measures.light_sensor import LightIntensity
from sensors_and_measures.moisture_sensor import SoilMoisture
from sensors_and_measures.tempearature_and_humidity_sensor import AirHumidity, AirTemperature


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
