import logging
import time
import threading

from grove.gpio import GPIO

MAX_WATERING_DURATION_SEC = 60  # Maximum watering duration in seconds (5 minutes)
MAX_ATOMIZING_DURATION_SEC = 600  # Maximum watering duration in seconds (5 minutes)


class GreenhouseControlSignal:
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"


class DeviceType:
    PUMP = "pump"
    LCD = "lcd"
    ATOMIZER = "atomizer"


class DeviceControllerInterface:
    def control(self, signal: str):
        pass

class GreenhouseDeviceRegistry:
    def __init__(self):
        self.controllers = {}


    def register_controller(self, controller: DeviceControllerInterface) -> None:
        self.controllers[controller.controller_type] = controller


    def get_controller(self, controller_type: str):
        return self.controllers.get(controller_type, None)


class WaterAtomizerController:
    def __init__(self):
        self.controller_type = DeviceType.ATOMIZER
    pass


class WaterPumpButton(GPIO):
    pass
    

class WaterPumpController(GPIO, DeviceControllerInterface):  
    def __init__(self, pump_gpio_pin: int = None, watering_duration_sec: int = 5):
        if pump_gpio_pin is None:
            raise ValueError("Pump GPIO pin must be provided")
        
        self.controller_type = DeviceType.PUMP
        
        if watering_duration_sec <= 0 or watering_duration_sec > MAX_WATERING_DURATION_SEC:
            logging.warning(f"Watering duration must be between 1 and {MAX_WATERING_DURATION_SEC} seconds. Setting to default 5 seconds.")
            watering_duration_sec = 5
        
        self.watering_duration_sec = watering_duration_sec
        self._stop_signal = True
        self._pump_thread = None
        super().__init__(pump_gpio_pin, GPIO.OUT)
        self.write(0)  # Ensure pump is off initially

    def update_watering_duration(self, watering_duration_sec: int):
        """Update the watering duration dynamically"""
        if watering_duration_sec <= 0 or watering_duration_sec > MAX_WATERING_DURATION_SEC:
            logging.warning(f"Invalid watering duration: {watering_duration_sec}. Keeping current value: {self.watering_duration_sec}")
            return
        
        old_duration = self.watering_duration_sec
        self.watering_duration_sec = watering_duration_sec
        logging.info(f"Updated watering duration: {old_duration} -> {watering_duration_sec} seconds")


    def control(self, signal: str):
        if signal.lower() == GreenhouseControlSignal.TURN_ON:
            self._start_control_thread()
        elif signal.lower() == GreenhouseControlSignal.TURN_OFF:
            self._turn_off()
        else:
            logging.warning(f"Unknown pump control signal: {signal}")


    def _start_control_thread(self):
        if self._pump_thread and self._pump_thread.is_alive():
            logging.info("Pump is already running.")
            return

        self._stop_signal = False
        self._pump_thread = threading.Thread(target=self._turn_on, daemon=True)
        self._pump_thread.start()


    def _turn_on(self):
        start_time = time.time()
        self.write(1)  # Turn on the pump
        logging.info("Water pump turned ON")    
        while time.time() - start_time < MAX_WATERING_DURATION_SEC:
            logging.debug("Watering...")
            if self._stop_signal:
                logging.info("Watering stopped by stop signal.")
                break
            time.sleep(5)
        self.write(0) # Turn off the pump
        logging.info("Watering completed")


    def _turn_off(self):
        self._stop_signal = True
        if hasattr(self, "_pump_thread") and self._pump_thread.is_alive():
            logging.info("Water pump turned OFF")
        else:
            logging.info("Water pump is already OFF")