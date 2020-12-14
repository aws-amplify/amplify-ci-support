#!/usr/bin/env python3

from aws_cdk import core
from stacks.amplify_deployer_stack import AmplifyDeployer

def build_amplify_deployer_stack_props(cb_project_name: str, 
                                        github_repo: str, 
                                        github_owner: str, 
                                        branch: str,
                                        shell_script_name: str):
    props = {}
    props['cb_project_name'] = cb_project_name
    props['shell_script_name'] = shell_script_name
    props['github_repo'] = github_repo
    if github_owner is not None:
        props['github_owner'] = github_owner
    if branch is not None:
        props['branch'] = branch
    return props

app = core.App()
github_owner=app.node.try_get_context("github_owner")
branch=app.node.try_get_context("branch")

TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
if TARGET_ACCOUNT is None or TARGET_REGION is None:
    raise Exception("Context variables region and account are required.")

TARGET_ENV = core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)
GITHUB_REPO = 'amplify-ci-support'
BANNER_TEXT = f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}"
SEPARATOR = "-" * len(BANNER_TEXT)

print(SEPARATOR)
print(BANNER_TEXT)
print(SEPARATOR)

instrumented_test_props = build_amplify_deployer_stack_props(cb_project_name="DataStoreTestsBackendDeployer",
                                                    github_repo=GITHUB_REPO,
                                                    github_owner=github_owner,
                                                    branch=branch,
                                                    shell_script_name="deploy_datastore_tests_backend.sh")

api_instrumented_test_props = build_amplify_deployer_stack_props(cb_project_name="ApiTestsBackendDeployer",
                                                    github_repo=GITHUB_REPO,
                                                    github_owner=github_owner,
                                                    branch=branch,
                                                    shell_script_name="deploy_api_tests_backend.sh")                                             

instrumented_test_backend_stack = AmplifyDeployer(app, "DataStoreTestsBackendDeployer", instrumented_test_props, env=TARGET_ENV)
api_instrumented_test_backend_stack = AmplifyDeployer(app, "ApiTestsBackendDeployer", api_instrumented_test_props, env=TARGET_ENV)

app.synth()
