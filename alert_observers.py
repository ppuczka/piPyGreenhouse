"""
Azure IoT Hub alert observer implementation.
Sends alerts to Azure IoT Hub when triggered by sensors.
"""

import logging
from typing import Optional
from alerts import Alert, AlertObserver
from azure_services import AzureIotHubMessage, AzureIotHubSignalType


class AzureIotHubAlertObserver(AlertObserver):
    
    def __init__(self, iot_hub_client=None):
        self.iot_hub_client = iot_hub_client
        self._enabled = True
        logging.info("Azure IoT Hub Alert Observer initialized")
    
    def set_iot_hub_client(self, iot_hub_client) -> None:
        self.iot_hub_client = iot_hub_client
        logging.info("IoT Hub client set for alert observer")
    
    def enable(self) -> None:
        self._enabled = True
        logging.info("Azure IoT Hub alert sending enabled")
    
    def disable(self) -> None:
        self._enabled = False
        logging.info("Azure IoT Hub alert sending disabled")
    
    def on_alert(self, alert: Alert) -> None:
        if not self._enabled:
            logging.debug("Alert sending disabled, skipping alert")
            return
            
        if not self.iot_hub_client:
            logging.error("IoT Hub client not available, cannot send alert")
            return
        
        try:
            alert_data = self._create_alert_message(alert)
            
            message = AzureIotHubMessage(
                message_type=AzureIotHubSignalType.ALERT,
                content=alert_data
            )
            
            self.iot_hub_client.send_telemetry(message)
            
            logging.info(f"Alert sent to Azure IoT Hub: {alert.alert_type.value} - {alert.message}")
            
        except Exception as e:
            logging.error(f"Failed to send alert to Azure IoT Hub: {e}")
    
    def _create_alert_message(self, alert: Alert) -> 'AlertMessage':
        return AlertMessage(alert)


class AlertMessage:
    
    def __init__(self, alert: Alert):
        self.alert_type = alert.alert_type.value
        self.severity = alert.severity.value
        self.message = alert.message
        self.sensor_name = alert.sensor_name
        self.current_value = alert.current_value
        self.threshold_value = alert.threshold_value
        self.timestamp = alert.timestamp.isoformat()
        self.metadata = alert.metadata
        
        import uuid
        self.id = str(uuid.uuid4())
    
    def to_cosmos_db_item(self) -> dict:
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "sensor_name": self.sensor_name,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "document_type": "alert"
        }