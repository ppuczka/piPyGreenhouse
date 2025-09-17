#!/usr/bin/python

import asyncio
import os
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv

from greenhouse import GreenhouseService
from containers import Container

@inject
async def main(greenhouse_service: GreenhouseService = Provide[Container.greenhouse_service]) -> None:
    await greenhouse_service.run_in_parallel()
          
          
if __name__ == '__main__':
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    asyncio.run(main())
