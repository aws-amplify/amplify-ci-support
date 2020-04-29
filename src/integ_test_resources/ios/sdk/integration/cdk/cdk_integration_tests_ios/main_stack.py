from aws_cdk import(
    core
)
from cdk_stack_extension import CDKStackExtension

class MainStack(CDKStackExtension):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def add_dependency_with_region_filter(self,
                                          stack: CDKStackExtension):
        if stack._supported_in_region:
            self.add_dependency(stack)
            print("dependency added to main on:", stack.stack_name)
