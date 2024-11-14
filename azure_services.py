import logging

from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient

from models import Greenhouse


class AzureCosmosDbClient:
    # for creating default_credential following env variables need to be set: "AZURE_CLIENT_ID, "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"P
    def __init__(self, database_uri: str, database_name: str, container_name: str):
        default_credential = DefaultAzureCredential()
        self.client = CosmosClient(database_uri, default_credential)
        self.database_name = database_name
        self.container_name = container_name
        logging.info(f"successfully initialized CosmosClient")
    
    
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
        
    