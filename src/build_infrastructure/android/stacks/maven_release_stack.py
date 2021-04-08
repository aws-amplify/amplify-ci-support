from aws_cdk import (
    core
)

from amplify_custom_resources import MavenPublisher

class MavenReleaseStack(core.Stack):
    def __init__(self, scope: core.App, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        required_props = ['github_source']
        for prop in required_props:
            if prop not in props:
                raise RuntimeError(f"Parameter {prop} is required.")
        
        codebuild_project_name_prefix = props['codebuild_project_name_prefix']

        github_source = props['github_source']
        owner = github_source['owner']
        repo = github_source['repo']
        base_branch = github_source['base_branch']


        MavenPublisher(self, "ReleasePublisher", project_name=f"{codebuild_project_name_prefix}-ReleasePublisher",
                                                   github_owner=owner, 
                                                   github_repo=repo, 
                                                   base_branch=base_branch,
                                                   buildspec_path="scripts/maven-release-publisher.yml")