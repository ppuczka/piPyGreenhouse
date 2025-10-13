#!/usr/bin/env python3
"""
Test script to demonstrate configuration updates via Azure IoT twin patches.

This script shows how the GreenhouseAppConfig can be updated dynamically
and how those changes propagate to all connected components without requiring
an application restart.
"""

import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime

# Simple mock of the GreenhouseAppConfig for testing
@dataclass
class GreenhouseAppConfig:
    temperature_lo: int
    temperature_high: int
    humidity_lo: int
    humidity_high: int
    soil_moisture_lo: int
    soil_moisture_high: int
    watering_duration_sec: int
    atomizing_duration_sec: int
    display_backlight_on: bool
    display_interval_sec: int
    telemetry_send_sec: int
    metric_read_sec: int
    alerting_sec: int

    def __post_init__(self):
        self._update_callbacks = []
    
    def register_update_callback(self, callback):
        """Register a callback that will be called when config is updated"""
        self._update_callbacks.append(callback)
    
    def update_from_twin_patch(self, patch: dict) -> bool:
        """Update configuration from Azure IoT twin patch and notify callbacks"""
        updated = False
        
        # Mapping twin property names to config field names
        field_mapping = {
            'temperature_lo': 'temperature_lo',
            'temperature_high': 'temperature_high',
            'humidity_lo': 'humidity_lo',
            'humidity_high': 'humidity_high',
            'soil_moisture_lo': 'soil_moisture_lo',
            'soil_moisture_high': 'soil_moisture_high',
            'watering_duration_sec': 'watering_duration_sec',
            'atomizing_duration_sec': 'atomizing_duration_sec',
            'display_backlight_on': 'display_backlight_on',
            'display_interval_sec': 'display_interval_sec',
            'telemetry_send_sec': 'telemetry_send_sec',
            'metric_read_sec': 'metric_read_sec',
            'alerting_sec': 'alerting_sec'
        }
        
        for twin_property, field_name in field_mapping.items():
            if twin_property in patch:
                old_value = getattr(self, field_name)
                new_value = patch[twin_property]
                
                # Validate and convert types
                try:
                    if field_name == 'display_backlight_on':
                        new_value = bool(new_value)
                    else:
                        new_value = int(new_value)
                        
                    setattr(self, field_name, new_value)
                    updated = True
                    print(f"Updated config {field_name}: {old_value} -> {new_value}")
                except (ValueError, TypeError) as e:
                    print(f"Failed to update config {field_name}: {e}")
        
        if updated:
            # Notify all registered callbacks
            for callback in self._update_callbacks:
                try:
                    callback(self)
                except Exception as e:
                    print(f"Error in config update callback: {e}")
                    
        return updated
    
    def to_dict(self):
        result = self.__dict__.copy()
        # Remove callbacks from the dict as they're not serializable
        result.pop('_update_callbacks', None)
        return result


class MockConfigManager:
    """Mock config manager for testing"""
    def on_config_updated(self, config):
        print("Config Manager: Configuration update received!")
        print("Config Manager: Would update all connected components...")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_config_updates():
    """Test the configuration update functionality"""
    
    # Create initial configuration (simulating what comes from app_defaults.ini)
    initial_config = GreenhouseAppConfig(
        temperature_lo=18,
        temperature_high=23,
        humidity_lo=45,
        humidity_high=60,
        soil_moisture_lo=30,
        soil_moisture_high=70,
        watering_duration_sec=10,
        atomizing_duration_sec=5,
        display_backlight_on=True,
        display_interval_sec=5,
        telemetry_send_sec=600,
        metric_read_sec=30,
        alerting_sec=300
    )
    
    print(f"Initial configuration:")
    print(json.dumps(initial_config.to_dict(), indent=2))
    print()
    
    # Create config manager
    config_manager = MockConfigManager()
    
    # Register callback
    initial_config.register_update_callback(config_manager.on_config_updated)
    
    # Simulate an Azure IoT twin desired properties patch
    # This is what would be received from Azure IoT Hub
    twin_patch = {
        "temperature_lo": 20,
        "temperature_high": 25,
        "watering_duration_sec": 15,
        "telemetry_send_sec": 300,
        "display_backlight_on": False
    }
    
    print(f"Simulating twin patch update:")
    print(json.dumps(twin_patch, indent=2))
    print()
    
    # Apply the update
    print("Applying configuration update...")
    updated = initial_config.update_from_twin_patch(twin_patch)
    
    if updated:
        print("Configuration successfully updated!")
        print(f"Updated configuration:")
        print(json.dumps(initial_config.to_dict(), indent=2))
    else:
        print("No configuration changes were made.")
        
    print()
    print("Test completed successfully!")


if __name__ == "__main__":
    test_config_updates()