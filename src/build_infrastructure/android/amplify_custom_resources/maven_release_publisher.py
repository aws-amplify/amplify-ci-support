
from aws_cdk import core
from aws_cdk.aws_codebuild import (
    BuildEnvironment,
    BuildSpec,
    ComputeType,
    EventAction,
    FilterGroup,
    LinuxBuildImage,
    Project,
    Source
)

class MavenPublisher(Project):
    BUILD_IMAGE = LinuxBuildImage.AMAZON_LINUX_2_3
    def __init__(self, scope: core.Construct, id: str, *,
                    project_name: str,
                    github_owner,
                    github_repo,
                    buildspec_path,
                    environment_variables = {},
                    base_branch: str = "main",
                    release_branch: str = "bump_version"):

        build_environment = BuildEnvironment(build_image=self.BUILD_IMAGE, privileged = True, compute_type = ComputeType.LARGE)

        trigger_on_pr_merged = FilterGroup.in_event_of(EventAction.PULL_REQUEST_MERGED).and_base_branch_is(base_branch).and_branch_is(release_branch).and_commit_message_is("release:.*")
            
        super().__init__(scope, id,
            project_name = project_name,
            environment_variables = environment_variables,
            build_spec=BuildSpec.from_source_filename(buildspec_path),
            badge = True,
            source = Source.git_hub(owner = github_owner,
                                    report_build_status = True,
                                    repo = github_repo, 
                                    webhook = True,
                                    webhook_filters = [trigger_on_pr_merged]),
            environment = build_environment)
