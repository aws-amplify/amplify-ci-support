#!/usr/bin/env python3

from aws_cdk import core
from cdk.distribution_stack import DistributionStack

app = core.App()

DistributionStack(app, "DistributionStack")

app.synth()
