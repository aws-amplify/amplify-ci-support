from aws_cdk import(
    core
)
from boto3.session import Session
import os

class CDKStackExtension(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._supported_in_region: bool

    def is_service_supported_in_region(self,
                                       service_name: str = None,
                                       region_name: str = None) -> bool:

        boto3_session = Session()
        if region_name is None:
            region_name = os.environ["CDK_DEFAULT_REGION"]

        if service_name is None:
            service_name = self.stack_name

        supported_regions_for_service = boto3_session.get_available_regions(service_name)
        service_supported_in_region = region_name in supported_regions_for_service
        return service_supported_in_region

    def are_services_supported_in_region(self,
                                         service_names: list,
                                         region_name: str = None) -> None:
        services_supported_in_region = True
        for service_name in service_names:
            services_supported_in_region = services_supported_in_region and \
                                               self.is_service_supported_in_region(service_name=service_name,
                                                                                   region_name=region_name)
        return services_supported_in_region

    @property
    def supported_in_region(self) -> bool:
        return self._supported_in_region

    @supported_in_region.setter
    def supported_in_region(self, value):
        self._supported_in_region = value