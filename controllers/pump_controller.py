import logging


class WaterPumpSignal:
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"

class WaterPumpController:
    def __init__(self, pump_gpio_pin):
        self.pump_gpio_pin = pump_gpio_pin
         # Ensure pump is off initially

    def turn_on(self):
        logging.info("Water pump turned ON")

    def turn_off(self):
        logging.info("Water pump turned OFF")