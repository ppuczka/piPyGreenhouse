# Greenhouse Alerting System Documentation

## Overview

The greenhouse monitoring system now includes a comprehensive alerting feature that automatically triggers alerts when sensor readings exceed predefined thresholds. The system uses the **Observer Pattern** to provide a flexible, extensible, and maintainable alerting architecture.

## Architecture

### Core Components

#### 1. Alert System (`alerts.py`)
- **Alert**: Data class representing an alert with type, severity, message, and metadata
- **AlertObserver**: Abstract base class for alert observers
- **AlertSubject**: Abstract base class for alert publishers (sensors)
- **AlertManager**: Manages alert cooldowns and deduplication
- **ThresholdConfig**: Configuration for threshold-based alerting
- **AlertSeverity**: Enumeration of alert severity levels
- **AlertType**: Enumeration of different alert types

#### 2. Alert Observers (`alert_observers.py`)
- **AzureIotHubAlertObserver**: Sends alerts to Azure IoT Hub
- **AlertMessage**: Wrapper for alert data transmission

#### 3. Enhanced Sensor Interface (`sensor_interface.py`)
- **SensorInterface**: Extended to inherit from AlertSubject
- Built-in threshold checking and alert triggering
- Error handling with automatic sensor error alerts

## How It Works

### Observer Pattern Implementation

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Sensors       │    │  Alert System    │    │   Observers     │
│  (Subjects)     │    │                  │    │                 │
│                 │    │ • ThresholdConfig│    │ • IoT Hub       │
│ • Temperature   │────│ • AlertManager   │────│ • Email         │
│ • Humidity      │    │ • Alert Creation │    │ • SMS           │
│ • Soil Moisture │    │                  │    │ • Dashboard     │
│ • Light         │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Alert Flow

1. **Sensor Reading**: Sensor takes a measurement
2. **Threshold Check**: Value compared against configured thresholds
3. **Alert Creation**: If threshold exceeded, Alert object created
4. **Observer Notification**: All registered observers notified
5. **Alert Processing**: Observers process alert (send to IoT Hub, log, etc.)
6. **Cooldown Management**: AlertManager prevents duplicate alerts

## Alert Types and Severity Levels

### Alert Types
- `TEMPERATURE_HIGH` / `TEMPERATURE_LOW`
- `HUMIDITY_HIGH` / `HUMIDITY_LOW`
- `SOIL_MOISTURE_HIGH` / `SOIL_MOISTURE_LOW`
- `LIGHT_INTENSITY_HIGH` / `LIGHT_INTENSITY_LOW`
- `SENSOR_ERROR`
- `SYSTEM_ERROR`

### Severity Levels
- `LOW`: Informational alerts
- `MEDIUM`: Important but not critical
- `HIGH`: Requires attention
- `CRITICAL`: Immediate action required

## Configuration

### Threshold Configuration Example

```python
from alerts import ThresholdConfig, AlertSeverity

temp_config = ThresholdConfig(
    low_threshold=18.0,          # Temperature below 18°C triggers alert
    high_threshold=28.0,         # Temperature above 28°C triggers alert
    low_severity=AlertSeverity.MEDIUM,
    high_severity=AlertSeverity.HIGH,
    cooldown_seconds=300,        # 5-minute cooldown between identical alerts
    enabled=True
)
```

### Default Sensor Configurations

#### Temperature & Humidity Sensor
```python
# Temperature thresholds
low_threshold: 18°C (MEDIUM severity)
high_threshold: 28°C (HIGH severity)
cooldown: 300 seconds (5 minutes)

# Humidity thresholds  
low_threshold: 40% (MEDIUM severity)
high_threshold: 70% (MEDIUM severity)
cooldown: 300 seconds (5 minutes)
```

#### Soil Moisture Sensor
```python
low_threshold: 30% (HIGH severity)    # Critical - needs watering
high_threshold: 80% (MEDIUM severity) # Less critical - overwatering
cooldown: 600 seconds (10 minutes)    # Slower changes
```

#### Light Intensity Sensor
```python
low_threshold: 100 lux (MEDIUM severity)
high_threshold: 800 lux (LOW severity)
cooldown: 900 seconds (15 minutes)    # Gradual changes
```

## Usage Examples

### 1. Basic Alert Setup

```python
from alerts import ThresholdConfig, AlertSeverity
from alert_observers import AzureIotHubAlertObserver

# Create alert observer
alert_observer = AzureIotHubAlertObserver()
alert_observer.set_iot_hub_client(iot_hub_client)

# Attach to sensor
sensor.attach(alert_observer)

# Configure thresholds
config = ThresholdConfig(
    low_threshold=20.0,
    high_threshold=30.0,
    low_severity=AlertSeverity.MEDIUM,
    high_severity=AlertSeverity.HIGH,
    cooldown_seconds=300,
    enabled=True
)
sensor.set_threshold_config(config)
```

### 2. Custom Alert Observer

```python
from alerts import AlertObserver, Alert

class EmailAlertObserver(AlertObserver):
    def on_alert(self, alert: Alert):
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            send_email(
                subject=f"Greenhouse Alert: {alert.alert_type.value}",
                body=alert.message,
                recipient="admin@greenhouse.com"
            )

# Use custom observer
email_observer = EmailAlertObserver()
sensor.attach(email_observer)
```

### 3. Dynamic Threshold Updates

```python
# Update thresholds via configuration
new_config = ThresholdConfig(
    low_threshold=15.0,  # New lower threshold
    high_threshold=32.0, # New upper threshold
    # ... other settings
)
sensor.set_threshold_config(new_config)
```

## Alert Data Structure

### Alert Object
```python
@dataclass
class Alert:
    alert_type: AlertType           # Type of alert (e.g., TEMPERATURE_HIGH)
    severity: AlertSeverity         # Severity level
    message: str                    # Human-readable message
    sensor_name: str               # Name of triggering sensor
    current_value: float           # Current sensor reading
    threshold_value: float         # Threshold that was exceeded
    timestamp: datetime            # When alert occurred
    metadata: dict                 # Additional context data
```

### Azure IoT Hub Alert Message
```json
{
  "id": "uuid-string",
  "alert_type": "temperature_high",
  "severity": "high",
  "message": "temperature is too high: 32.0 (threshold: 28.0)",
  "sensor_name": "TemperatureHumiditySensor",
  "current_value": 32.0,
  "threshold_value": 28.0,
  "timestamp": "2025-10-16T21:49:42.755366",
  "metadata": {
    "threshold_type": "high",
    "measurement_type": "temperature"
  },
  "document_type": "alert"
}
```

## Integration with Existing System

### Sensor Integration
All sensors automatically inherit alerting capabilities:

```python
class MySensor(SensorInterface):
    def __init__(self):
        super().__init__()  # Inherits alerting functionality
        
    def get_measurements(self):
        value = self.read_sensor()
        
        # Automatic threshold checking
        self.check_thresholds(value, "my_measurement")
        
        return value
```

### Container Configuration
The dependency injection container automatically wires alert observers:

```python
# In containers.py
alert_observer = providers.Singleton(AzureIotHubAlertObserver)

configured_alert_observer = providers.Factory(
    setup_sensor_alerting,
    alert_observer,
    soil_moisture_sensor,
    temp_and_humidity_sensor,
    light_intensity_sensor
)
```

## Alert Management Features

### 1. Cooldown Management
Prevents alert spam by enforcing minimum time between identical alerts:

```python
# AlertManager automatically handles cooldowns
alert_key = f"{sensor_name}_{measurement_type}_{threshold_type}"
if alert_manager.should_send_alert(alert_key, cooldown_seconds):
    # Send alert
    pass
else:
    # Alert suppressed due to cooldown
    pass
```

### 2. Alert History
Each sensor maintains a history of recent alerts:

```python
# Get alert history for a sensor
alert_history = sensor.get_alert_history()
for alert in alert_history:
    print(f"{alert.timestamp}: {alert.message}")
```

### 3. Error Handling
Automatic sensor error alerts when readings fail:

```python
def get_measurements(self):
    try:
        value = self.read_sensor()
        return value
    except Exception as e:
        # Automatic error alert
        self.trigger_sensor_error_alert(str(e))
        return None
```

## Monitoring and Debugging

### Logging
Comprehensive logging throughout the alert system:

```
2025-10-16 21:49:42 - INFO - Alert observer attached: AzureIotHubAlertObserver
2025-10-16 21:49:42 - INFO - Notifying 1 observers about alert: temperature_high
2025-10-16 21:49:42 - INFO - Alert sent to Azure IoT Hub: temperature_high - temperature is too high: 32.0
```

### Testing
Use the provided test script to verify alerting functionality:

```bash
python test_alerting_simple.py
```

## Best Practices

### 1. Threshold Selection
- **Temperature**: Consider plant requirements and seasonal variations
- **Humidity**: Balance mold prevention with plant needs
- **Soil Moisture**: Critical for plant health - lower thresholds more important
- **Light**: Account for daily cycles and growth stages

### 2. Severity Assignment
- **CRITICAL**: Immediate plant health threats (extreme conditions)
- **HIGH**: Important conditions requiring prompt attention
- **MEDIUM**: Notable deviations from optimal conditions
- **LOW**: Informational alerts for trend monitoring

### 3. Cooldown Configuration
- **Fast-changing values** (temperature): Shorter cooldowns (5-15 minutes)
- **Slow-changing values** (soil moisture): Longer cooldowns (10-30 minutes)
- **Very stable values** (light): Extended cooldowns (15-60 minutes)

### 4. Observer Design
- Keep observers lightweight and non-blocking
- Handle exceptions gracefully to prevent disrupting other observers
- Consider async operations for external notifications

### 5. Testing
- Test all threshold combinations
- Verify cooldown functionality
- Test error conditions and sensor failures
- Validate alert message formatting

## Performance Considerations

### Memory Usage
- Alert history is limited to 100 entries per sensor
- AlertManager maintains minimal state for cooldowns
- Observers should not accumulate unlimited data

### Processing Overhead
- Threshold checking is O(1) operation
- Observer notification is O(n) where n = number of observers
- Consider batch processing for high-frequency sensors

### Network Impact
- Azure IoT Hub alerts are sent asynchronously
- Failed alert transmissions are logged but don't block sensor readings
- Consider alert aggregation for very active systems

## Troubleshooting

### Common Issues

#### 1. Alerts Not Triggering
- Verify threshold configuration is enabled
- Check threshold values are appropriate for sensor readings
- Ensure observers are properly attached
- Verify sensor is calling `check_thresholds()`

#### 2. Duplicate Alerts
- Check cooldown configuration
- Verify AlertManager is working correctly
- Review alert keys for uniqueness

#### 3. Missing IoT Hub Alerts
- Verify IoT Hub client is connected
- Check Azure credentials and connection string
- Review network connectivity
- Monitor IoT Hub logs

#### 4. Performance Issues
- Review alert frequency and cooldown settings
- Check for blocking operations in observers
- Monitor memory usage with alert history

### Debugging Steps

1. **Enable Debug Logging**
   ```python
   logging.getLogger().setLevel(logging.DEBUG)
   ```

2. **Check Alert History**
   ```python
   history = sensor.get_alert_history()
   print(f"Recent alerts: {len(history)}")
   ```

3. **Test Threshold Logic**
   ```python
   sensor.check_thresholds(test_value, "test_measurement")
   ```

4. **Verify Observer Attachment**
   ```python
   print(f"Observers attached: {len(sensor._observers)}")
   ```

## Future Enhancements

### Planned Features
- **Alert Aggregation**: Combine multiple related alerts
- **Smart Thresholds**: ML-based adaptive thresholds
- **Alert Escalation**: Automatic severity escalation over time
- **Multi-channel Observers**: Email, SMS, push notifications
- **Alert Dashboard**: Web-based alert monitoring
- **Alert Rules Engine**: Complex conditional alerting logic

### Integration Opportunities
- **Weather Integration**: Adjust thresholds based on weather
- **Plant Growth Stage**: Modify alerts based on growth phase
- **Seasonal Adjustments**: Automatic threshold updates by season
- **Remote Configuration**: Update thresholds via IoT Hub device twins