from abc import ABC, abstractmethod
from typing import Any, Optional
from alerts import AlertSubject, Alert, AlertType, AlertSeverity, ThresholdConfig, alert_manager


class AlertState:
    OK = "OK"
    ALERTING = "ALERTING"


class SensorInterface(AlertSubject, ABC):
    
    def __init__(self):
        super().__init__()
        self.sensor_name = self.__class__.__name__
        self._threshold_config: Optional[ThresholdConfig] = None
    
    @abstractmethod
    def get_measurements(self) -> Any:
        pass
    
    def set_threshold_config(self, config: ThresholdConfig) -> None:
        self._threshold_config = config
    
    def check_thresholds(self, value: float, measurement_type: str) -> None:
        if not self._threshold_config or not self._threshold_config.enabled:
            return
        
        alert = None
        
        if (self._threshold_config.high_threshold is not None and 
            value > self._threshold_config.high_threshold):
            
            alert_key = f"{self.sensor_name}_{measurement_type}_high"
            if alert_manager.should_send_alert(alert_key, self._threshold_config.cooldown_seconds):
                alert = Alert(
                    alert_type=self._get_alert_type(measurement_type, "high"),
                    severity=self._threshold_config.high_severity,
                    message=f"{measurement_type} is too high: {value} (threshold: {self._threshold_config.high_threshold})",
                    sensor_name=self.sensor_name,
                    current_value=value,
                    threshold_value=self._threshold_config.high_threshold,
                    metadata={"threshold_type": "high", "measurement_type": measurement_type}
                )
        
        # Check low threshold
        elif (self._threshold_config.low_threshold is not None and 
              value < self._threshold_config.low_threshold):
            
            alert_key = f"{self.sensor_name}_{measurement_type}_low"
            if alert_manager.should_send_alert(alert_key, self._threshold_config.cooldown_seconds):
                alert = Alert(
                    alert_type=self._get_alert_type(measurement_type, "low"),
                    severity=self._threshold_config.low_severity,
                    message=f"{measurement_type} is too low: {value} (threshold: {self._threshold_config.low_threshold})",
                    sensor_name=self.sensor_name,
                    current_value=value,
                    threshold_value=self._threshold_config.low_threshold,
                    metadata={"threshold_type": "low", "measurement_type": measurement_type}
                )
        
        if alert:
            self.notify_observers(alert)
    
    def _get_alert_type(self, measurement_type: str, threshold_type: str) -> AlertType:
        """Map measurement type and threshold type to AlertType enum"""
        mapping = {
            ("temperature", "high"): AlertType.TEMPERATURE_HIGH,
            ("temperature", "low"): AlertType.TEMPERATURE_LOW,
            ("humidity", "high"): AlertType.HUMIDITY_HIGH,
            ("humidity", "low"): AlertType.HUMIDITY_LOW,
            ("soil_moisture", "high"): AlertType.SOIL_MOISTURE_HIGH,
            ("soil_moisture", "low"): AlertType.SOIL_MOISTURE_LOW,
            ("light_intensity", "high"): AlertType.LIGHT_INTENSITY_HIGH,
            ("light_intensity", "low"): AlertType.LIGHT_INTENSITY_LOW,
        }
        
        return mapping.get((measurement_type.lower(), threshold_type), AlertType.SYSTEM_ERROR)
    
    def trigger_sensor_error_alert(self, error_message: str) -> None:
        """Trigger an alert for sensor errors"""
        alert = Alert(
            alert_type=AlertType.SENSOR_ERROR,
            severity=AlertSeverity.HIGH,
            message=f"Sensor error in {self.sensor_name}: {error_message}",
            sensor_name=self.sensor_name,
            current_value=0.0,
            metadata={"error_type": "sensor_error", "error_message": error_message}
        )
        self.notify_observers(alert)
    
    def alert(self) -> AlertState:
        """Legacy method - kept for backwards compatibility"""
        return AlertState.OK
        