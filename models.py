import uuid
from datetime import datetime
from sensors_and_measures.soil_moisture import SoilMoisture
from sensors_and_measures.tempearature_and_humidity_sensor import AirHumidity, AirTemperature


class Greenhouse:
    def __init__(self, soil_moisture: SoilMoisture, air_temperature: AirTemperature, air_humidity: AirHumidity):
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.soil_moisture = soil_moisture
        self.air_temperature = air_temperature
        self.air_humidity = air_humidity
        
        _uuid = uuid.uuid4()
        self.id = _uuid.hex 
     
        
    def to_cosmos_db_item(self): 
        return {
            "id": self.id,
            "temperature": self.air_temperature.temperature,
            "temperature_level": self.air_temperature.temperature_level.value,
            "humidity": self.air_humidity.humidity,
            "humidity_lever": self.air_humidity.humidity_level.value,
            "soil_moisture": self.soil_moisture.sensor_value,
            "soil_moisture_level": self.soil_moisture.moisture_level.value,
            "date_time": self.datetime
            }


    def display_measure(self): return f'''Date & time: {self.datetime}
                        Soil moisture (value: {self.soil_moisture.sensor_value}, moisture_level: {self.soil_moisture.moisture_level})
                        Air temperature (value: {self.air_temperature.temperature}, temperature_level: {self.air_temperature.temperature_level}) 
                        Air humidity (value: {self.air_humidity.humidity}, humidity_level: {self.air_humidity.humidity_level}) '''
