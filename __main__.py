#!/usr/bin/python

import os
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv

from greenhouse import GreenhouseService
from containers import Container

load_dotenv('.env')

@inject
def main(greenhouse_service: GreenhouseService = Provide[Container.greenhouse_service]) -> None:
    greenhouse_service.start_measuring()
          
          
if __name__ == '__main__':
    print("Sffffdsfsdfsdfsdfdsf")
    print(os.getcwd())
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    main()