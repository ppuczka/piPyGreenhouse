import logging
from dependency_injector.wiring import Provide, inject

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
    logging.info("test")
    container.wire(modules=[__name__])
    main()