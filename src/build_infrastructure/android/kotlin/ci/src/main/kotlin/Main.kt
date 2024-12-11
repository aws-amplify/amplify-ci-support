import software.amazon.awscdk.App
import testing.TestInfrastuctureStack

fun main() {
    val app = App()

    TestInfrastuctureStack(app, "TestInfrastructureStack").create()

    app.synth()
}