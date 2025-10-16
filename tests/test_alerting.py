#!/usr/bin/env python3
"""
Test script to demonstrate the alerting feature using the Observer pattern.

This script simulates sensor readings that would trigger alerts and shows
how the alerts are processed and sent to Azure IoT Hub.
"""

import logging
import json
from datetime import datetime
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Mock classes for testing without hardware dependencies
class MockAzureIotHubMessage:
    def __init__(self, message_type, content):
        self.message_type = message_type
        self.content = content

class MockIotHubClient:
    """Mock IoT Hub client for testing"""
    def __init__(self):
        self.sent_messages = []
        
    def send_telemetry(self, message):
        """Mock telemetry sending"""
        print(f"📤 ALERT SENT TO IOT HUB:")
        print(f"   Type: {message.message_type}")
        print(f"   Content: {json.dumps(message.content.to_cosmos_db_item(), indent=2)}")
        print("   ✅ Alert successfully transmitted to Azure IoT Hub")
        print("-" * 60)
        self.sent_messages.append(message)

# Import our actual alert classes
from alerts import Alert, AlertType, AlertSeverity, ThresholdConfig, alert_manager
from alert_observers import AzureIotHubAlertObserver, AlertMessage


class MockSensor:
    """Mock sensor for testing alerting"""
    def __init__(self, name: str, threshold_config: ThresholdConfig):
        self.name = name
        self.threshold_config = threshold_config
        self.observers = []
        
    def attach(self, observer):
        self.observers.append(observer)
        
    def notify_observers(self, alert: Alert):
        for observer in self.observers:
            observer.on_alert(alert)
    
    def simulate_reading(self, value: float, measurement_type: str):
        """Simulate a sensor reading and check for alerts"""
        print(f"📊 {self.name} reading: {value} ({measurement_type})")
        
        alert = None
        
        # Check high threshold
        if (self.threshold_config.high_threshold is not None and 
            value > self.threshold_config.high_threshold):
            
            alert_key = f"{self.name}_{measurement_type}_high"
            if alert_manager.should_send_alert(alert_key, self.threshold_config.cooldown_seconds):
                alert = Alert(
                    alert_type=AlertType.TEMPERATURE_HIGH if measurement_type == "temperature" else AlertType.HUMIDITY_HIGH,
                    severity=self.threshold_config.high_severity,
                    message=f"{measurement_type} is too high: {value} (threshold: {self.threshold_config.high_threshold})",
                    sensor_name=self.name,
                    current_value=value,
                    threshold_value=self.threshold_config.high_threshold,
                    metadata={"threshold_type": "high", "measurement_type": measurement_type}
                )
        
        # Check low threshold
        elif (self.threshold_config.low_threshold is not None and 
              value < self.threshold_config.low_threshold):
            
            alert_key = f"{self.name}_{measurement_type}_low"
            if alert_manager.should_send_alert(alert_key, self.threshold_config.cooldown_seconds):
                alert = Alert(
                    alert_type=AlertType.TEMPERATURE_LOW if measurement_type == "temperature" else AlertType.HUMIDITY_LOW,
                    severity=self.threshold_config.low_severity,
                    message=f"{measurement_type} is too low: {value} (threshold: {self.threshold_config.low_threshold})",
                    sensor_name=self.name,
                    current_value=value,
                    threshold_value=self.threshold_config.low_threshold,
                    metadata={"threshold_type": "low", "measurement_type": measurement_type}
                )
        
        if alert:
            print(f"🚨 ALERT TRIGGERED: {alert.message}")
            self.notify_observers(alert)
        else:
            print(f"✅ Reading within normal range")
        
        print()


def main():
    print("🌱 Greenhouse Alert System Test")
    print("=" * 60)
    
    # Create mock IoT Hub client
    iot_client = MockIotHubClient()
    
    # Create alert observer
    alert_observer = AzureIotHubAlertObserver()
    alert_observer.set_iot_hub_client(iot_client)
    
    # Patch the AzureIotHubMessage class to use our mock
    import alert_observers
    alert_observers.AzureIotHubMessage = MockAzureIotHubMessage
    
    # Create mock sensors with threshold configurations
    temp_config = ThresholdConfig(
        low_threshold=18.0,
        high_threshold=28.0,
        low_severity=AlertSeverity.MEDIUM,
        high_severity=AlertSeverity.HIGH,
        cooldown_seconds=0,  # No cooldown for testing
        enabled=True
    )
    
    humidity_config = ThresholdConfig(
        low_threshold=40.0,
        high_threshold=70.0,
        low_severity=AlertSeverity.MEDIUM,
        high_severity=AlertSeverity.MEDIUM,
        cooldown_seconds=0,  # No cooldown for testing
        enabled=True
    )
    
    soil_moisture_config = ThresholdConfig(
        low_threshold=30.0,
        high_threshold=80.0,
        low_severity=AlertSeverity.HIGH,
        high_severity=AlertSeverity.MEDIUM,
        cooldown_seconds=0,  # No cooldown for testing
        enabled=True
    )
    
    # Create mock sensors
    temp_sensor = MockSensor("TemperatureSensor", temp_config)
    humidity_sensor = MockSensor("HumiditySensor", humidity_config)
    soil_sensor = MockSensor("SoilMoistureSensor", soil_moisture_config)
    
    # Attach alert observer to all sensors
    temp_sensor.attach(alert_observer)
    humidity_sensor.attach(alert_observer)
    soil_sensor.attach(alert_observer)
    
    print("🔗 Alert observer attached to all sensors")
    print()
    
    # Test scenarios
    print("📋 Testing Alert Scenarios:")
    print("-" * 30)
    
    # Normal readings - should not trigger alerts
    print("1. Normal readings (no alerts expected):")
    temp_sensor.simulate_reading(22.5, "temperature")
    humidity_sensor.simulate_reading(55.0, "humidity")  
    soil_sensor.simulate_reading(50.0, "soil_moisture")
    
    # High temperature alert
    print("2. High temperature alert:")
    temp_sensor.simulate_reading(32.0, "temperature")
    
    # Low humidity alert
    print("3. Low humidity alert:")
    humidity_sensor.simulate_reading(25.0, "humidity")
    
    # Critical low soil moisture alert
    print("4. Critical low soil moisture alert:")
    soil_sensor.simulate_reading(15.0, "soil_moisture")
    
    # High soil moisture alert
    print("5. High soil moisture alert:")
    soil_sensor.simulate_reading(85.0, "soil_moisture")
    
    # Low temperature alert
    print("6. Low temperature alert:")
    temp_sensor.simulate_reading(12.0, "temperature")
    
    # Summary
    print("📊 Test Summary:")
    print(f"   Total alerts sent to IoT Hub: {len(iot_client.sent_messages)}")
    print("   Alert types sent:")
    for i, msg in enumerate(iot_client.sent_messages, 1):
        alert_data = msg.content.to_cosmos_db_item()
        print(f"   {i}. {alert_data['alert_type']} - {alert_data['severity']}")
    
    print("\n✅ Alert system test completed successfully!")
    print("   All alerts were processed and would be sent to Azure IoT Hub.")


if __name__ == "__main__":
    main()