import os
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient

class AzureCosmosDbClient:
    
    # for creating default_credential following env variables need to be set: "AZURE_CLIENT_ID, "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"P
    def __init__(self):
        default_credential = DefaultAzureCredential()
        self.client = CosmosClient("https://pi-greenhouse.documents.azure.com:443/", default_credential)
    
    
    def test(self):
        db_client = self.client.get_database_client("pi-greenhouse")
        container_client = db_client.get_container_client("greenhouse")
       
       
    def list_contailers(self, database_name: str):
        db_client = self.client.get_database_client(database_name)
        return db_client.list_containers()