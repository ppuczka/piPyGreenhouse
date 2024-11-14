from dependency_injector.wiring import Provide, inject

from greenhouse import GreenhouseService
from containers import Container


@inject
def main(greenhouse_service: GreenhouseService = Provide[Container.greenhouse_service]) -> None:
    greenhouse_service.start_measuring(interval_in_minutes=5)
          
          
if __name__ == '__main__':
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    main()