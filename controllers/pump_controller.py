import logging
import time
import threading

MAX_WATERING_DURATION_SEC = 60  # Maximum watering duration in seconds (5 minutes)


class WaterPumpSignal:
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"


class WaterPumpController:
        
    def __init__(self, pump_gpio_pin):
        self.pump_gpio_pin = pump_gpio_pin
        self._stop_signal = True
        self._pump_thread = None


    def control_pump(self, signal: str):
        if signal.lower() == WaterPumpSignal.TURN_ON:
            self._start_watering_thread()
        elif signal.lower() == WaterPumpSignal.TURN_OFF:
            self._turn_off()
        else:
            logging.warning(f"Unknown pump control signal: {signal}")


    def _start_watering_thread(self):
        if self._pump_thread and self._pump_thread.is_alive():
            logging.info("Pump is already running.")
            return
        
        self._stop_signal = False
        self._pump_thread = threading.Thread(target=self._turn_on, daemon=True)
        self._pump_thread.start()


    def _turn_on(self):
        start_time = time.time()
        while time.time() - start_time < MAX_WATERING_DURATION_SEC:
            logging.debug("Watering...")
            if self._stop_signal:
                logging.info("Watering stopped by stop signal.")
                break
            time.sleep(1)  # Simulate pump running
        logging.info("Watering completed")


    def _turn_off(self):
        self._stop_signal = True
        if hasattr(self, "_pump_thread") and self._pump_thread.is_alive():
            logging.info("Water pump turned OFF")
        else:
            logging.info("Water pump is already OFF")