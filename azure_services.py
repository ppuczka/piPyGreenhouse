import json
import logging
import threading
import uuid

from azure.identity import DefaultAzureCredential
from azure.iot.device import IoTHubDeviceClient, Message
from azure.cosmos import CosmosClient

from models import Greenhouse


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


class AzureIotHubMessageType:
    METRICS = "metrics"
    ALERT = "alert"
    COMMAND = "command"


class AzureIotHubMessage:
    def __init__(self, message_type: AzureIotHubMessageType, content: object):
        self.id = content.id if hasattr(content, 'id') else str(uuid.uuid4())
        self.message = Message(json.dumps(content.to_cosmos_db_item()))
        self.message.content_encoding = "utf-8"
        self.message.content_type = "application/json"
        self.message.custom_properties = {"type": message_type}
        self.message.message_id = self.id
        logging.info(f"Azure IoT Hub Message created with ID: {self.id} and type: {message_type}")
        
        
class AzureIotHubClient:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
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


    def send_telemetry(self, iotMessage: AzureIotHubMessage):        
        try:
            self.client.send_message(iotMessage.message)
            logging.info("Telemetry sent to IoT Hub")
        except Exception as e:
            logging.error(f"Failed to send telemetry: {e}")

    
    def start_receiving_messages(self, message_handler=None):
        def receive_loop():
            logging.info("Message receive loop started.")
            while True:
                try:
                    message = self.client.receive_message()  # blocking call
                    logging.info(f"Received message from IoT Hub: {message.data}")
                    if message_handler:
                        message_handler(message)
                except Exception as e:
                    logging.error(f"Error receiving message: {e}")
                    break  # or continue, depending on your needs

        logging.info("Starting message receive loop...")
        thread = threading.Thread(target=receive_loop, daemon=True)
        thread.start()
        
        
class AzureIotHubClientException(Exception):
    pass