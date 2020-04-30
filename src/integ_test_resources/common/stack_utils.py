from common.common_stack import CommonStack


def add_stack_dependency_on_common_stack(stacks_in_app: list,
                                         common_stack: CommonStack):
    for stack in stacks_in_app:
        stack.add_dependency(common_stack)
