from constructs import Construct

from common.region_aware_stack import RegionAwareStack


class MainStack(RegionAwareStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def add_dependency_with_region_filter(self, stack: RegionAwareStack):
        if stack.supported_in_region:
            self.add_dependency(stack)
            print("dependency added to main on:", stack.stack_name)
