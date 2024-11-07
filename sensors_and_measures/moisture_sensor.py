import logging
from grove.adc import ADC
from .soil_moisture import SoilMoisture

__all__ = ["SoilMoistureSensor"]


class SoilMoistureSensor:
    '''
    Grove Moisture Sensor class

    Args:
        pin(int): number of analog pin/channel the sensor connected.
    '''
    def __init__(self, pin: int):
        self.channel = pin
        self.adc = ADC()

    @property
    def moisture(self):
        '''
        Get the moisture strength value/voltage

        Returns:
            (int): voltage, in mV
        '''
        value = self.adc.read_voltage(self.channel)
        return value
     
    def get_soil_moisture(self):
        print('Detecting moisture...')
        return SoilMoisture(self.moisture)
    