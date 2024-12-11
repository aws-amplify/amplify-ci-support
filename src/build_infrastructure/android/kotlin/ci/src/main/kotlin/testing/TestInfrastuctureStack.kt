package testing

import software.amazon.awscdk.Stack
import software.amazon.awscdk.StackProps
import software.constructs.Construct
import util.SecretIdentifier

class TestInfrastuctureStack
    @JvmOverloads
    constructor(
        scope: Construct,
        id: String,
        props: StackProps? = null,
    ) : Stack(scope, id, props) {
        private val githubPat =
            SecretIdentifier(
                secretName = "github/pat/amplify-android",
                secretKey = "amplify_android_pat",
            )

        fun create() {
            createUnitTestProject()
            createUiUnitTestProject()
        }

        private fun createUnitTestProject() {
            val check =
                PullRequestCheck(
                    name = "AmplifyAndroid-UnitTest",
                    description = "Runs unit tests for amplify-android repository",
                    buildSpecFilePath = "buildspecs/unit_test.yml",
                    owner = "mattcreaser",
                    repository = "amplify-android",
                    githubPatSecret = githubPat,
                )
            check.create(this)
        }

        private fun createUiUnitTestProject() {
            val check =
                PullRequestCheck(
                    name = "Amplify-UI-Android-Build",
                    description = "Runs unit tests for the amplify-ui-android repository",
                    buildSpecFilePath = "buildspecs/ui_unit_test.yml",
                    owner = "mattcreaser",
                    repository = "amplify-ui-android",
                    githubPatSecret = githubPat,
                )
            check.create(this)
        }
    }
