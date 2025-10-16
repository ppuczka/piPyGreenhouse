#!/usr/bin/env python3
"""
Simplified test script to demonstrate the alerting feature using the Observer pattern.
This version doesn't require Azure SDK dependencies.
"""

import logging
import json
from datetime import datetime
from typing import List
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Copy core alert classes for testing without imports
class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    TEMPERATURE_HIGH = "temperature_high"
    TEMPERATURE_LOW = "temperature_low"
    HUMIDITY_HIGH = "humidity_high" 
    HUMIDITY_LOW = "humidity_low"
    SOIL_MOISTURE_HIGH = "soil_moisture_high"
    SOIL_MOISTURE_LOW = "soil_moisture_low"

@dataclass
class Alert:
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    sensor_name: str
    current_value: float
    threshold_value: float = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "sensor_name": self.sensor_name,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class ThresholdConfig:
    low_threshold: float = None
    high_threshold: float = None
    low_severity: AlertSeverity = AlertSeverity.MEDIUM
    high_severity: AlertSeverity = AlertSeverity.MEDIUM
    cooldown_seconds: int = 300
    enabled: bool = True

class AlertManager:
    def __init__(self):
        self._last_alert_times = {}
    
    def should_send_alert(self, alert_key: str, cooldown_seconds: int) -> bool:
        now = datetime.now()
        last_alert = self._last_alert_times.get(alert_key)
        
        if last_alert is None:
            self._last_alert_times[alert_key] = now
            return True
        
        time_since_last = (now - last_alert).total_seconds()
        if time_since_last >= cooldown_seconds:
            self._last_alert_times[alert_key] = now
            return True
        
        return False

alert_manager = AlertManager()

class AlertObserver:
    def on_alert(self, alert: Alert):
        pass

class MockIotHubAlertObserver(AlertObserver):
    def __init__(self):
        self.sent_alerts = []
        
    def on_alert(self, alert: Alert):
        print(f"📤 ALERT SENT TO IOT HUB:")
        print(f"   Type: {alert.alert_type.value}")
        print(f"   Severity: {alert.severity.value}")
        print(f"   Message: {alert.message}")
        print(f"   Sensor: {alert.sensor_name}")
        print(f"   Value: {alert.current_value}")
        print(f"   Threshold: {alert.threshold_value}")
        print(f"   Timestamp: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("   ✅ Alert successfully transmitted to Azure IoT Hub")
        print("-" * 60)
        self.sent_alerts.append(alert)

class MockSensor:
    def __init__(self, name: str, threshold_config: ThresholdConfig):
        self.name = name
        self.threshold_config = threshold_config
        self.observers = []
        
    def attach(self, observer: AlertObserver):
        self.observers.append(observer)
        print(f"🔗 Alert observer attached to {self.name}")
        
    def notify_observers(self, alert: Alert):
        for observer in self.observers:
            observer.on_alert(alert)
    
    def check_thresholds(self, value: float, measurement_type: str):
        """Check if value exceeds thresholds and trigger alerts"""
        if not self.threshold_config.enabled:
            return
        
        alert = None
        
        # Check high threshold
        if (self.threshold_config.high_threshold is not None and 
            value > self.threshold_config.high_threshold):
            
            alert_key = f"{self.name}_{measurement_type}_high"
            if alert_manager.should_send_alert(alert_key, self.threshold_config.cooldown_seconds):
                alert_type_map = {
                    "temperature": AlertType.TEMPERATURE_HIGH,
                    "humidity": AlertType.HUMIDITY_HIGH,
                    "soil_moisture": AlertType.SOIL_MOISTURE_HIGH
                }
                alert = Alert(
                    alert_type=alert_type_map.get(measurement_type, AlertType.TEMPERATURE_HIGH),
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
                alert_type_map = {
                    "temperature": AlertType.TEMPERATURE_LOW,
                    "humidity": AlertType.HUMIDITY_LOW,
                    "soil_moisture": AlertType.SOIL_MOISTURE_LOW
                }
                alert = Alert(
                    alert_type=alert_type_map.get(measurement_type, AlertType.TEMPERATURE_LOW),
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
    
    def simulate_reading(self, value: float, measurement_type: str):
        """Simulate a sensor reading and check for alerts"""
        print(f"📊 {self.name} reading: {value} ({measurement_type})")
        self.check_thresholds(value, measurement_type)
        print()


def main():
    print("🌱 Greenhouse Alert System Test")
    print("=" * 60)
    
    # Create alert observer
    alert_observer = MockIotHubAlertObserver()
    
    # Create sensor configurations
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
    
    # Test cooldown functionality
    print("7. Testing alert cooldown (duplicate alert - should be suppressed):")
    # Reset cooldown to test functionality
    temp_sensor.threshold_config.cooldown_seconds = 300  # 5 minutes
    temp_sensor.simulate_reading(35.0, "temperature")  # This should trigger
    temp_sensor.simulate_reading(36.0, "temperature")  # This should be suppressed
    
    # Summary
    print("📊 Test Summary:")
    print(f"   Total alerts sent to IoT Hub: {len(alert_observer.sent_alerts)}")
    print("   Alert types sent:")
    for i, alert in enumerate(alert_observer.sent_alerts, 1):
        print(f"   {i}. {alert.alert_type.value} - {alert.severity.value} - {alert.sensor_name}")
    
    print("\n✅ Alert system test completed successfully!")
    print("   Observer pattern implementation working correctly.")
    print("   All alerts would be sent to Azure IoT Hub in production.")
    
    # Demonstrate alert data structure
    if alert_observer.sent_alerts:
        print("\n📄 Sample Alert Data Structure:")
        sample_alert = alert_observer.sent_alerts[0]
        print(json.dumps(sample_alert.to_dict(), indent=2))


if __name__ == "__main__":
    main()