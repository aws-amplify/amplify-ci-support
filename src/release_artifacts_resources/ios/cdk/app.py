#!/usr/bin/env python3

from aws_cdk import core
from cdk.credential_rotation_stack import CredentialRotationStack
from cdk.distribution_stack import DistributionStack

app = core.App()
distribution_stack = DistributionStack(app, "DistributionStack")
credential_rotation_stack = CredentialRotationStack(app, "CredentialRotationStack")

app.synth()
