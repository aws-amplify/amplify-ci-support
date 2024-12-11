package testing

import software.amazon.awscdk.SecretValue
import software.amazon.awscdk.SecretsManagerSecretOptions
import software.amazon.awscdk.services.codebuild.*
import software.amazon.awscdk.services.logs.LogGroup
import util.SecretIdentifier

class PullRequestCheck(
    private val name: String,
    private val description: String,
    private val buildSpecFilePath: String,
    private val repository: String,
    private val githubPatSecret: SecretIdentifier,
    private val owner: String = "aws-amplify",
    private val branch: String = "main"
) {
    private val actorIds = listOf(
        "2781254", // mattcreaser
        "10183120", // sktimalsina
        "634763", // tylerjroach
        "766908", // vincetran
        "105604551", // edisooon
        "46607340", // awsmobilesdk bot
        "41898282" // github-actions[bot]
    )

    fun create(stack: TestInfrastuctureStack) {
        // Create the build environment (image, size, etc)
        val environment =
            BuildEnvironment
                .builder()
                .buildImage(LinuxBuildImage.AMAZON_LINUX_2_4)
                .computeType(ComputeType.LARGE)
                .build()


        val buildSpec = BuildSpec.fromAsset(buildSpecFilePath)

        val cloudwatch = CloudWatchLoggingOptions.builder()
            .logGroup(LogGroup(stack, "/aws/codebuild/$name"))
            .build()
        val logging = LoggingOptions.builder()
            .cloudWatch(cloudwatch)
            .build()

        val source = setupGithub(stack)

        Project.Builder.create(stack, name)
            .projectName(name)
            .description(description)
            .environment(environment)
            .source(source)
            .buildSpec(buildSpec)
            .logging(logging)
            .badge(true) // enable the build badge for display on repository README
            .build()
    }

    private fun setupGithub(stack: TestInfrastuctureStack): ISource {
        val githubPat = SecretValue.secretsManager(githubPatSecret.secretName, SecretsManagerSecretOptions.builder().jsonField(githubPatSecret.secretKey).build())
        GitHubSourceCredentials.Builder.create(stack, "$repository-Credentials")
            .accessToken(githubPat)
            .build()


        val webhookFilters = listOf(
            FilterGroup.inEventOf(EventAction.PULL_REQUEST_CREATED, EventAction.PULL_REQUEST_UPDATED)
                .andBaseRefIs("^refs/heads/main\$")
                .andActorAccountIs("^(${actorIds.joinToString("|")})\$")
        )

        val sourceProps = GitHubSourceProps.builder()
            .owner(owner)
            .repo(repository)
            .cloneDepth(1)
            .branchOrRef(branch)
            .webhook(true)
            .reportBuildStatus(true)
            .webhookFilters(webhookFilters)
            .build()
        return Source.gitHub(sourceProps)
    }
}