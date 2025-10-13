import json
import logging
import threading
from typing import Optional
import uuid

from azure.identity import DefaultAzureCredential
from azure.iot.device import IoTHubDeviceClient, Message
from azure.cosmos import CosmosClient

from models import Greenhouse
from controllers.greenhouse_controllers import DeviceControllerInterface, GreenhouseDeviceRegistry, WaterPumpController

class AzureIotHubSignalType:
    METRICS = "metrics"
    ALERT = "alert"
    COMMAND = "command"
    MESSAGE = "message"
    TWINS = "twins"              
            
class AzureIotHubClientException(Exception):
    pass


class AzureCosmosDbClient:
    # for creating default_credential following env variables need to be set: "AZURE_CLIENT_ID, "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"P
    def __init__(self, database_uri: str, database_name: str, container_name: str):
        default_credential = DefaultAzureCredential()
        self.client = CosmosClient(database_uri, default_credential)
        self.database_name = database_name
        self.container_name = container_name
        logging.info(f"Azure CosmosDbClient initialized for database: {database_name}, container: {container_name}")
    
    
    def insert_measure(self, measure: Greenhouse):
        container = self._get_container_client()
        item = measure.to_cosmos_db_item()
        result = container.create_item(body=item)
        return result
          

    def get_database_containers(self):
        db_client = self.client.get_database_client(self.database_name)
        return db_client.list_containers()
    
   
    def _get_container_client(self):
        db_client = self.client.get_database_client(self.database_name)
        return db_client.get_container_client(self.container_name)


class AzureIotHubMessage:
    def __init__(self, message_type: AzureIotHubSignalType, content: object):
        self.id = content.id if hasattr(content, 'id') else str(uuid.uuid4())
        self.message = Message(json.dumps(content.to_cosmos_db_item()))
        self.message.content_encoding = "utf-8"
        self.message.content_type = "application/json"
        self.message.custom_properties = {"type": message_type}
        self.message.message_id = self.id
        logging.info(f"Azure IoT Hub Message created with ID: {self.id} and type: {message_type}")
        

class AzureIotHubIncomingSignalHandler:
    def __init__(self, greenhouse_controller_registry: GreenhouseDeviceRegistry, app_config=None):
        self.greenhouse_controller_registry = greenhouse_controller_registry
        self.app_config = app_config
        logging.info("Azure IoT Hub Incoming Signal Handler initialized.")
        
        
    def handle_incoming_signal(self, message: Message):
        if message is None or message.data == "":
            logging.info("Received empty message from IoT Hub.")
            return
        
        data = message.data.decode().lower() if hasattr(message.data, 'decode') else str(message.data)
        if data == AzureIotHubSignalType.COMMAND:
            logging.info("Received command message from IoT Hub.")
            command_properties = {k.lower(): v for k, v in message.custom_properties.items()}
            self._handle_command(command_properties)
            return
        
        if data == AzureIotHubSignalType.MESSAGE:
            logging.info("Received general message from IoT Hub.")
            message_properties = {k.lower(): v for k, v in message.custom_properties.items()}
            self._handle_message(message_properties)
            return

        logging.warning("Unknown signal received.")
        return
            

    def _handle_message(self, properties: dict):
        logging.info("Handling message signal...")


    def _handle_command(self, properties: dict):
        logging.info("Handling command signal...")
        for signal_type, value in properties.items():
            controller: DeviceControllerInterface = self.greenhouse_controller_registry.get_controller(signal_type)
            if controller:
                logging.info(f"Executing command '{value}' on controller '{signal_type}'")
                controller.control(value)
                return
            else:
                logging.warning(f"No controller found for signal: {signal_type}")
        return

    def _handle_twin_update(self, patch):
        """Handle twin desired properties patch updates"""
        logging.info(f"Processing twin patch update: {patch}")
        
        if self.app_config is None:
            logging.warning("No app_config provided to handle twin updates")
            return
            
        try:
            # Update the configuration with the patch
            updated = self.app_config.update_from_twin_patch(patch)
            if updated:
                logging.info("Configuration updated successfully from twin patch")
            else:
                logging.info("No configuration changes made from twin patch")
        except Exception as e:
            logging.error(f"Error handling twin update: {e}")
            return
    
# Use different handlers for direct device connection and Iot Twins    
class AzureIotHubClient:
    def __init__(self, signal_handler: AzureIotHubIncomingSignalHandler,  connection_string: str):
        self.connection_string = connection_string
        self.signal_handler = signal_handler
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        self.twin_update_callback = None
        self._twin_update_thread = None
        self._twin_update_interval = 30 
        self._running = False
        self._current_metrics = None
        self._device_status = {}
        logging.info("Azure IoT Hub Client initialized.")    
    
    def connect(self):
        try:
            self.client.connect()
            
            self.client.on_message_received = self._on_message_received
            self.client.on_twin_desired_properties_patch_received = self._on_twin_patch_received

            logging.info("Connected to Azure IoT Hub with twins support.")
        except Exception as e:
            logging.error(f"Failed to connect to IoT Hub: {e}")
            raise AzureIotHubClientException("Failed to connect to IoT Hub") from e


    def disconnect(self):
        try:
            self.client.disconnect()
            logging.info("Disconnected from Azure IoT Hub.")
        except Exception as e:
            logging.error(f"Failed to disconnect from IoT Hub: {e}")
            raise AzureIotHubClientException("Failed to disconnect from IoT Hub") from e


    def send_telemetry(self, iotMessage: AzureIotHubMessage):        
        try:
            self.client.send_message(iotMessage.message)
            logging.info("Telemetry sent to IoT Hub")
        except Exception as e:
            logging.warning(f"Failed to send telemetry: {e}")
    
    
    def update_twin_properties(self, reported_properties: dict):
        try:
            self.client.patch_twin_reported_properties(reported_properties)
            logging.info("Twin reported properties updated.")
        except Exception as e:
            logging.warning(f"Failed to update twin properties: {e}")
    
    
    def get_device_twin(self):
        try:
            twin = self.client.get_twin()
            logging.info("Device twin retrieved.")
            return twin
        except Exception as e:
            logging.warning(f"Failed to get device twin: {e}")
            return None
    
    
    def _on_twin_patch_received(self, patch):
            logging.info(f"Twin patch received: {patch}")
            if self.signal_handler:
                self.signal_handler._handle_twin_update(patch)    


    def _on_message_received(self, message) -> Optional[Message]:
        try:
            logging.info(f"Received message from IoT Hub: {message.data}")
            self.signal_handler.handle_incoming_signal(message)
        except Exception as e:
            logging.warning(f"Error receiving message: {e}")
            return None
        
