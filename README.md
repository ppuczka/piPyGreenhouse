# 🌱 PiPyGreenhouse - Smart IoT Greenhouse Management System

A comprehensive IoT greenhouse management system built with Python for Raspberry Pi, featuring Azure IoT Hub integration, real-time monitoring, and automated environmental control.

## 🚀 Features

### 📊 Environmental Monitoring
- **Temperature & Humidity**: Real-time air temperature and humidity monitoring with DHT sensors
- **Soil Moisture**: Continuous soil moisture level tracking with analog sensors
- **Light Intensity**: Ambient light measurement for optimal plant growth conditions
- **LCD Display**: Live environmental data display with customizable intervals

### 🤖 Automated Controls
- **Smart Watering**: Automated irrigation based on soil moisture levels
- **Water Atomization**: Humidity control through misting system
- **Threshold-Based Actions**: Configurable environmental thresholds trigger automated responses

### ☁️ Azure IoT Integration
- **Real-time Telemetry**: Continuous data streaming to Azure IoT Hub
- **Device Twins**: Remote configuration management without application restarts
- **Cloud Storage**: Data persistence in Azure Cosmos DB
- **Command & Control**: Remote device control via Azure IoT Hub messages

### 🔧 Dynamic Configuration
- **Live Updates**: Change thresholds, intervals, and settings remotely via Azure IoT Device Twins
- **No Downtime**: Configuration changes apply immediately without restarting the application
- **Validation**: Built-in parameter validation and error handling
- **Comprehensive Logging**: Detailed logging of all configuration changes and system events

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Sensors       │    │  Raspberry Pi    │    │   Azure Cloud   │
│                 │    │                  │    │                 │
│ • DHT22         │────│ GreenhouseService│────│ • IoT Hub       │
│ • Soil Moisture │    │                  │    │ • Cosmos DB     │
│ • Light Sensor  │    │ • Data Collection│    │ • Device Twins  │
│ • LCD Display   │    │ • Control Logic  │    │ • Telemetry     │
└─────────────────┘    │ • IoT Client     │    └─────────────────┘
                       └──────────────────┘
┌─────────────────┐    
│  Controllers    │    
│                 │    
│ • Water Pump    │────┤
│ • Atomizer      │    
│ • LCD Control   │    
└─────────────────┘    
```

## 🛠️ Hardware Requirements

### Required Components
- **Raspberry Pi** (3B+ or newer recommended)
- **Grove Base Hat** for Raspberry Pi
- **DHT22** Temperature & Humidity Sensor
- **Capacitive Soil Moisture Sensor**
- **Light Intensity Sensor (Analog)**
- **16x2 LCD Display** (I2C)
- **Water Pump** with relay module
- **Water Atomizer/Misting System**

### Optional Components
- **Manual Control Buttons**
- **LED Status Indicators**
- **Additional Sensors** (pH, EC, etc.)

## 🔌 Pin Configuration

| Component | Pin | Type |
|-----------|-----|------|
| DHT22 | GPIO 5 | Digital |
| Soil Moisture | A0 | Analog |
| Light Sensor | A2 | Analog |
| Water Pump | GPIO 22 | Digital |
| LCD Display | I2C | I2C |
| Control Button | GPIO 16 | Digital |

## 📋 Prerequisites

### Software Requirements
- Python 3.8 or higher
- Raspberry Pi OS (Bullseye or newer)
- I2C enabled on Raspberry Pi

### Azure Requirements
- Azure subscription
- Azure IoT Hub instance
- Azure Cosmos DB account (optional)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ppuczka/piPyGreenhouse.git
cd piPyGreenhouse
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Hardware Setup
- Connect all sensors and actuators according to the pin configuration
- Enable I2C: `sudo raspi-config` → Interface Options → I2C → Enable

### 4. Configuration

#### Environment Variables
Create a `.env` file:
```bash
AZURE_IOT_HUB_CONNECTION_STRING="your_connection_string_here"
AZURE_CLIENT_ID="your_client_id"
AZURE_CLIENT_SECRET="your_client_secret"
AZURE_TENANT_ID="your_tenant_id"
```

#### Application Settings
Edit `config.ini` and `app_defaults.ini` to match your hardware setup and preferences.

### 5. Run the Application
```bash
python -m piPyGreenhouse
```

## 🔧 Configuration

### Static Configuration Files

- **`config.ini`**: Hardware pin assignments and Azure connection settings
- **`app_defaults.ini`**: Default thresholds, intervals, and operational parameters

### Dynamic Configuration (Azure IoT Device Twins)

Update configuration remotely without restarting:

```json
{
  "properties": {
    "desired": {
      "temperature_lo": 20,
      "temperature_high": 25,
      "humidity_lo": 50,
      "humidity_high": 70,
      "soil_moisture_lo": 30,
      "soil_moisture_high": 80,
      "watering_duration_sec": 15,
      "telemetry_send_sec": 300,
      "metric_read_sec": 60
    }
  }
}
```

For detailed configuration options, see [CONFIG_UPDATES.md](CONFIG_UPDATES.md).

## 📊 Monitoring & Data

### Real-time Display
- Environmental metrics on LCD display
- System uptime and status
- Configurable display intervals

### Cloud Telemetry
- Automatic data transmission to Azure IoT Hub
- Configurable transmission intervals
- JSON-formatted sensor data with timestamps

### Data Storage
- Optional Azure Cosmos DB integration
- Local logging with rotation
- Structured data format for analytics

## 🎮 Remote Control

### Device Commands
Send commands via Azure IoT Hub:

```json
{
  "data": "command",
  "custom_properties": {
    "pump": "turn_on",
    "atomizer": "turn_off",
    "lcd": "turn_on"
  }
}
```

### Supported Commands
- `pump`: `turn_on`, `turn_off`
- `atomizer`: `turn_on`, `turn_off`  
- `lcd`: `turn_on`, `turn_off`

## 🔍 Troubleshooting

### Common Issues

#### Grove Base Hat Not Detected
```bash
# Check I2C address (should be 0x08)
sudo i2cdetect -y 1
```

If you see address 0x04, edit the grove library:
```bash
# Edit .venv/lib/python3.11/site-packages/grove/adc.py line 50
# Change address from 0x04 to 0x08
```

#### Sensor Reading Errors
- Verify all connections are secure
- Check power supply voltage (should be 3.3V or 5V as required)
- Ensure Grove Base Hat is properly seated

#### Azure Connection Issues
- Verify connection string is correct
- Check network connectivity
- Ensure IoT Hub is accessible from your network

### Logging
Monitor application logs for detailed troubleshooting:
```bash
tail -f /var/log/greenhouse.log
```

## 🚀 Deployment Options

### Development Mode
```bash
python -m piPyGreenhouse
```

### SystemD Service
Install as a system service:
```bash
sudo cp os/greenhouse.service /etc/systemd/system/
sudo systemctl enable greenhouse
sudo systemctl start greenhouse
```

### Cron Job
Run at regular intervals:
```bash
# Add to crontab
*/15 * * * * cd /path/to/piPyGreenhouse && python -m piPyGreenhouse
```

## 🏗️ Architecture Details

### Design Patterns
- **Dependency Injection**: Clean separation of concerns using dependency-injector
- **Singleton Pattern**: Shared configuration and service instances
- **Observer Pattern**: Configuration update callbacks
- **Factory Pattern**: Device controller registry

### Key Components

#### Core Services
- **`GreenhouseService`**: Main application orchestrator
- **`AzureIotHubClient`**: Azure IoT Hub communication
- **`AzureCosmosDbClient`**: Database operations
- **`GreenhouseConfigManager`**: Configuration update coordination

#### Sensors & Actuators
- **`TemperatureHumiditySensor`**: DHT22 interface
- **`SoilMoistureSensor`**: Analog moisture sensor interface  
- **`LightIntensitySensor`**: Analog light sensor interface
- **`WaterPumpController`**: Pump control with safety limits
- **`LcdDisplay`**: Display management with dynamic updates

#### Configuration Management
- **`GreenhouseAppConfig`**: Configuration model with validation
- **`AzureIotHubIncomingSignalHandler`**: IoT message processing
- **Dynamic Updates**: Live configuration changes via Azure Device Twins

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Configuration Update Testing
```bash
python test_config_updates.py
```

### Hardware Testing
```bash
python -m piPyGreenhouse --test-mode
```

## 📚 API Reference

### Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `temperature_lo` | int | Lower temperature threshold (°C) | 18 |
| `temperature_high` | int | Upper temperature threshold (°C) | 23 |
| `humidity_lo` | int | Lower humidity threshold (%) | 45 |
| `humidity_high` | int | Upper humidity threshold (%) | 60 |
| `soil_moisture_lo` | int | Lower soil moisture threshold (%) | 30 |
| `soil_moisture_high` | int | Upper soil moisture threshold (%) | 70 |
| `watering_duration_sec` | int | Watering duration (seconds) | 10 |
| `atomizing_duration_sec` | int | Atomizing duration (seconds) | 5 |
| `display_interval_sec` | int | Display update interval (seconds) | 5 |
| `telemetry_send_sec` | int | Telemetry transmission interval (seconds) | 600 |
| `metric_read_sec` | int | Sensor reading interval (seconds) | 30 |


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 📈 Roadmap

### Upcoming Features
- [ ] Mobile app for monitoring and control
- [ ] Machine learning-based optimization
- [ ] Weather integration
- [ ] Multi-zone greenhouse support
- [ ] Advanced analytics dashboard
- [ ] Camera integration for plant monitoring
- [ ] pH and EC sensor support
- [ ] Automated nutrient dosing


## 🏆 Acknowledgments

- [Grove.py](https://github.com/Seeed-Studio/grove.py) - Sensor interface library
- [Azure IoT SDK](https://github.com/Azure/azure-iot-sdk-python) - Azure IoT integration
- [dependency-injector](https://github.com/ets-labs/python-dependency-injector) - Dependency injection framework

