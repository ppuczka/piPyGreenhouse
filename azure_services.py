import json
import logging
import threading
from typing import Optional
import uuid

from azure.identity import DefaultAzureCredential
from azure.iot.device import IoTHubDeviceClient, Message
from azure.cosmos import CosmosClient

from models import Greenhouse
from controllers.pump_controller import WaterPumpController

class AzureIotHubSignalType:
    METRICS = "metrics"
    ALERT = "alert"
    COMMAND = "command"
    MESSAGE = "message"
        
        
class ControlSignal:
    PUMP = "pump"
    LCD = "lcd"
    
            
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
    def __init__(self, water_pump_controller: WaterPumpController):
        self.water_pump_controller = water_pump_controller
        
        
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
        # Lowercase all custom property keys for case-insensitive matching
        if ControlSignal.PUMP in properties.keys():
            logging.info(f"Pump control signal received: {properties[ControlSignal.PUMP]}")
            self.water_pump_controller.control_pump(properties[ControlSignal.PUMP])
            logging.info(f"Pump control signal executed: {properties[ControlSignal.PUMP]}")
            return
        
        if ControlSignal.LCD in properties.keys():
            logging.info(f"LCD control signal received: {properties[ControlSignal.LCD]}")
            return
        logging.warning("Unknown command signal received.")
        return
    
    
class AzureIotHubClient:
    def __init__(self, signal_handler: AzureIotHubIncomingSignalHandler, connection_string: str):
        self.connection_string = connection_string
        self.signal_handler = signal_handler
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        logging.info("Azure IoT Hub Client initialized.")
    
    
    def connect(self):
        try:
            self.client.connect()
            logging.info("Connected to Azure IoT Hub.")
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
    
    
    def receive_message(self) -> Optional[Message]:
        try:
            message = self.client.receive_message()  # blocking call
            logging.info(f"Received message from IoT Hub: {message.data}")
            return message
        except Exception as e:
            logging.warning(f"Error receiving message: {e}")
            return None
        
    
    def start_receiving_messages(self):
        def receive_loop():
            logging.info("Message receive loop started.")
            while True:
                logging.info("Message receive loop started.")
                message = self.receive_message()
                if message:
                    self.signal_handler.handle_incoming_signal(message)
                    
        thread = threading.Thread(target=receive_loop, daemon=True)
        thread.start()
