import logging
import os
from dependency_injector.wiring import Provide, inject

from azure_services import AzureCosmosDbClient
from greenhouse import GreenhouseService
from containers import Container


@inject
def main(
        greenhouse_service: GreenhouseService = Provide[Container.greenhouse_service]
        ) -> None:
            greenhouse_service.measure()
    
if __name__ == '__main__':
    container = Container()
    container.init_resources()
    client_id = os.getenv("CLIENT_ID")
    az_client = AzureCosmosDbClient()
    az_client.test()

    # container.wire(modules=[__name__])
    # main()