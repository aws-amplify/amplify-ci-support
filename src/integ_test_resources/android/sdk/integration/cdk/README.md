Each test suite has a separate CDK stack that can be used to set up the resources required to run that test suite.

Let's take aws-android-sdk-pinpoint-test as an example. To bring up the resources required (which for this test suite are a Pinpoint application and a Cognito identity pool), run the following:

$ npm install -g aws-cdk
$ cd integ_test_resources/android-sdk/cdk_integration_tests_android
$ pip install -r requirements.txt    # Best to do this in a virtualenv
$ cdk synth PinpointStack            # Synthesizes the CloudFormation template
$ cdk deploy PinpointStack           # Deploys the CloudFormation template

# Afterwards
$ cdk destroy
