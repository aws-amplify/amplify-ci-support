plugins {
    kotlin("jvm") version "2.0.10"
    application
}

dependencies {
    implementation(libs.aws.cdk)
}

tasks.test {
    useJUnitPlatform()
}
kotlin {
    jvmToolchain(21)
}

application {
    mainClass.set("MainKt")
}