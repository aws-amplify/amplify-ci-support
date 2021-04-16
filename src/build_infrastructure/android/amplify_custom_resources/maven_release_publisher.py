
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

BUILD_SPEC = {
   "version": 0.2,
   "env": {
      "shell": "/bin/sh",
      "secrets-manager": {
         "ORG_GRADLE_PROJECT_SONATYPE_NEXUS_USERNAME": "awsmobilesdk/android/sonatype:username",
         "ORG_GRADLE_PROJECT_SONATYPE_NEXUS_PASSWORD": "awsmobilesdk/android/sonatype:password",
         "ORG_GRADLE_PROJECT_signingPassword": "awsmobilesdk/android/signing:password",
         "ORG_GRADLE_PROJECT_signingKeyId": "awsmobilesdk/android/signing:keyId",
         "ORG_GRADLE_PROJECT_signingInMemoryKey": "awsmobilesdk/android/signing:inMemoryKey"
      }
   },
   "phases": {
      "build": {
         "commands": [
            "echo 'Build phase starting.'",
            "JAVA_HOME=$JDK_8_HOME ./gradlew clean build\nfor task_name in $(./gradlew tasks --all | grep uploadArchives | cut -d \" \" -f 1); do\n  echo \"Gradle task $task_name\"\n  JAVA_HOME=$JDK_8_HOME ./gradlew $task_name;\ndone\n"
         ],
         "finally": [
            "echo 'Build phase completed.'"
         ]
      },
      "post_build": {
         "commands": [
            "echo 'Post-build phase starting'"
         ],
         "finally": [
            "echo 'Post-build phase completed.'"
         ]
      }
   }
}

class MavenPublisher(Project):
    BUILD_IMAGE = LinuxBuildImage.AMAZON_LINUX_2_3
    def __init__(self, scope: core.Construct, id: str, *,
                    project_name: str,
                    github_owner,
                    github_repo,
                    buildspec_path = None,
                    environment_variables = {},
                    base_branch: str = "main",
                    release_branch: str = "bump_version",
                    create_webhooks = False):

        build_environment = BuildEnvironment(build_image=self.BUILD_IMAGE, privileged = True, compute_type = ComputeType.LARGE)

        trigger_on_pr_merged = FilterGroup.in_event_of(EventAction.PULL_REQUEST_MERGED).and_base_branch_is(base_branch).and_branch_is(release_branch).and_commit_message_is("release:.*")

        if create_webhooks:
            github_source = Source.git_hub(owner = github_owner,
                                            report_build_status = True,
                                            repo = github_repo,
                                            webhook = True,
                                            webhook_filters = [trigger_on_pr_merged])
        else:
            github_source = Source.git_hub(owner = github_owner,
                                            report_build_status = True,
                                            repo = github_repo)
            
        super().__init__(scope, id,
            project_name = project_name,
            environment_variables = environment_variables,
            build_spec=BuildSpec.from_object_to_yaml(BUILD_SPEC) if buildspec_path is None else BuildSpec.from_source_filename(buildspec_path),
            badge = True,
            source = github_source,
            environment = build_environment)
