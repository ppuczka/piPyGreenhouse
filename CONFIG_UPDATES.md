# Dynamic Configuration Updates via Azure IoT Device Twins

This document explains how to update your Greenhouse application configuration dynamically via Azure IoT Device Twins without requiring an application restart.

## Overview

The greenhouse application now supports dynamic configuration updates through Azure IoT Device Twins. When you update the desired properties in Azure IoT Hub, the changes automatically propagate to all relevant components in your application.

## How It Works

1. **GreenhouseAppConfig**: Extended with callback registration and twin patch processing
2. **ConfigManager**: Coordinates updates across all application components  
3. **IoT Hub Integration**: Receives twin updates and applies them to the configuration
4. **Component Updates**: All sensors, controllers, and services automatically receive the new settings

## Supported Configuration Parameters

All the following parameters can be updated via Azure IoT Device Twins:

### Temperature & Humidity Thresholds
- `temperature_lo`: Lower temperature threshold (°C)
- `temperature_high`: Upper temperature threshold (°C)  
- `humidity_lo`: Lower humidity threshold (%)
- `humidity_high`: Upper humidity threshold (%)

### Soil Moisture Thresholds
- `soil_moisture_lo`: Lower soil moisture threshold (%)
- `soil_moisture_high`: Upper soil moisture threshold (%)

### Controller Settings
- `watering_duration_sec`: Water pump duration in seconds
- `atomizing_duration_sec`: Atomizer duration in seconds

### Display Settings
- `display_backlight_on`: LCD backlight on/off (true/false)
- `display_interval_sec`: Display update interval in seconds

### Timing Intervals
- `telemetry_send_sec`: Telemetry transmission interval in seconds
- `metric_read_sec`: Sensor reading interval in seconds
- `alerting_sec`: Alert checking interval in seconds

## Usage Examples

### 1. Update Temperature Thresholds

To update temperature thresholds via Azure IoT Hub:

```json
{
  "properties": {
    "desired": {
      "temperature_lo": 20,
      "temperature_high": 25
    }
  }
}
```

### 2. Adjust Watering Settings

```json
{
  "properties": {
    "desired": {
      "watering_duration_sec": 15,
      "soil_moisture_lo": 25,
      "soil_moisture_high": 75
    }
  }
}
```

### 3. Change Display Settings

```json
{
  "properties": {
    "desired": {
      "display_backlight_on": false,
      "display_interval_sec": 10
    }
  }
}
```

### 4. Modify Telemetry Intervals

```json
{
  "properties": {
    "desired": {
      "telemetry_send_sec": 300,
      "metric_read_sec": 60
    }
  }
}
```

## How to Update Configuration

### Using Azure Portal

1. Navigate to your IoT Hub in the Azure Portal
2. Go to IoT devices and select your greenhouse device
3. Click on "Device Twin"
4. Add or modify properties in the `desired` section
5. Save the changes

### Using Azure CLI

```bash
# Update multiple properties
az iot hub device-twin update \
  --device-id your-device-id \
  --hub-name your-iot-hub-name \
  --set properties.desired.temperature_lo=20 \
       properties.desired.temperature_high=25 \
       properties.desired.watering_duration_sec=15
```

### Using Azure IoT Explorer

1. Open Azure IoT Explorer
2. Connect to your IoT Hub
3. Select your device
4. Go to "Device Twin"
5. Edit the desired properties
6. Save changes

## What Happens When Configuration Updates

When you update the device twin desired properties:

1. **Azure IoT Hub** sends the update to your device
2. **AzureIotHubClient** receives the twin patch
3. **AzureIotHubIncomingSignalHandler** processes the update
4. **GreenhouseAppConfig** updates its values and triggers callbacks
5. **GreenhouseConfigManager** propagates changes to all components:
   - **Sensors** get new thresholds
   - **Controllers** get new duration settings
   - **LCD Display** updates interval and backlight settings
   - **GreenhouseService** updates timing intervals

## Application Components Affected

### Sensors
- `SoilMoistureSensor`: Updates moisture thresholds
- `TemperatureHumiditySensor`: Updates temperature and humidity thresholds

### Controllers  
- `WaterPumpController`: Updates watering duration
- `LcdDisplay`: Updates display interval and backlight settings

### Services
- `GreenhouseService`: Updates measurement and telemetry intervals

## Validation and Error Handling

The system includes validation for all configuration updates:

- **Type checking**: Ensures numeric values are integers, booleans are valid
- **Range validation**: Some values have minimum/maximum limits (e.g., watering duration)
- **Error logging**: Invalid updates are logged but don't crash the application
- **Graceful degradation**: If one parameter fails to update, others still proceed

## Monitoring Configuration Changes

All configuration changes are logged with detailed information:

```
2024-XX-XX XX:XX:XX - INFO - Updated config temperature_lo: 18 -> 20
2024-XX-XX XX:XX:XX - INFO - Updated soil moisture thresholds: high=75, lo=25
2024-XX-XX XX:XX:XX - INFO - Configuration update propagation completed
```

## Best Practices

1. **Test changes gradually**: Update one or few parameters at a time
2. **Monitor logs**: Watch application logs after configuration changes
3. **Use reasonable values**: Ensure thresholds and intervals make sense for your setup
4. **Document changes**: Keep track of what changes were made and when
5. **Backup configurations**: Save working configurations before major changes

## Troubleshooting

### Configuration Updates Not Applied

- Check IoT Hub connectivity
- Verify device is receiving twin updates
- Check application logs for errors
- Ensure parameter names match exactly

### Invalid Values Rejected

- Check logs for specific validation errors
- Ensure numeric values are within reasonable ranges
- Verify boolean values are true/false

### Partial Updates

- Some parameters may update while others fail
- Check logs to see which specific parameters had issues
- Invalid parameters don't prevent valid ones from updating

## Testing Configuration Updates

You can test the configuration update functionality using the provided test script:

```bash
python test_config_updates.py
```

This demonstrates how twin patches are processed and applied to the configuration.