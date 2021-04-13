#!/usr/bin/env python3

import os
from aws_cdk import (
    core,
    aws_codepipeline_actions
)

from stacks.build_pipeline_stack import AmplifyAndroidCodePipeline
from stacks.account_bootstrap_stack import AccountBootstrap
from stacks.maven_release_stack import MavenReleaseStack

app = core.App()
SUPPORTED_LIBRARIES = {
    'amplify': {
        'repo': 'amplify-android',
        'owner': 'aws-amplify',
        'base_branch': 'main',
        'release_pr_branch': 'bump_version',
        'codebuild_project_name_prefix': 'AmplifyAndroid',
        'stack_name_prefix': '', # TODO: Re-create these with AmplifyAndroid as a prefix.
        'maven_deployer_buildspec': 'scripts/maven-release-publisher.yml',
        'create_webhooks': True
    },
    'v2-sdk' : {
        'repo': 'aws-sdk-android',
        'owner': 'aws-amplify',
        'base_branch': 'main',
        'release_pr_branch': 'bump_version',
        'codebuild_project_name_prefix': 'AndroidSDK',
        'stack_name_prefix': 'AndroidSDK-',
        'maven_deployer_buildspec': 'build-support/maven-release-publisher.yml',
        'create_webhooks': False
    },
    'appsync-sdk': {
        'repo': 'aws-mobile-appsync-sdk-android',
        'owner': 'awslabs',
        'base_branch': 'main',
        'release_pr_branch': 'bump_version',
        'codebuild_project_name_prefix': 'AndroidAppSyncSDK',
        'stack_name_prefix': 'AndroidAppSyncSDK-',
        'maven_deployer_buildspec': 'build-support/maven-release-publisher.yml',
        'create_webhooks': False
    }
}

LIBRARY = app.node.try_get_context("library")
if LIBRARY is None:
    raise RuntimeError(f'Context variable library must be one of these values: {SUPPORTED_LIBRARIES.keys()}')

SETTINGS = SUPPORTED_LIBRARIES[LIBRARY]

TARGET_REGION = app.node.try_get_context("region")
TARGET_ACCOUNT = app.node.try_get_context("account")
TARGET_ENV=core.Environment( account=TARGET_ACCOUNT, region=TARGET_REGION)

print(f"AWS Account={TARGET_ACCOUNT} Region={TARGET_REGION}")

# settings that are overridable via the command-line. Typically overrides are only needed during testing.
github_repo = app.node.try_get_context("github_repo") if app.node.try_get_context("github_repo") is not None else SETTINGS['repo']
github_owner = app.node.try_get_context("github_owner") if app.node.try_get_context("github_owner") is not None else SETTINGS['owner']
branch = app.node.try_get_context("branch") if app.node.try_get_context("branch") is not None else SETTINGS['base_branch']
release_pr_branch = app.node.try_get_context("release_pr_branch") if app.node.try_get_context("release_pr_branch") is not None else SETTINGS['release_pr_branch']

create_webhooks = SETTINGS['create_webhooks']
maven_deployer_buildspec = SETTINGS['maven_deployer_buildspec']

codebuild_project_name_prefix = SETTINGS['codebuild_project_name_prefix']
stack_name_prefix = SETTINGS['stack_name_prefix']

config_source_bucket = app.node.try_get_context("config_source_bucket")
log_level=app.node.try_get_context("log_level")

print(f'Github repo:{github_owner}/{github_repo} Branches: {branch} (Base branch) {release_pr_branch} (PR branch) Prefixes: {codebuild_project_name_prefix} (CodeBuild) {stack_name_prefix} (Stacks)')

# Account bootstrap stack
account_bootstrap = AccountBootstrap(app, 'AccountBootstrap', {}, env=TARGET_ENV)

# Pipeline stack with DeviceFarm tests is only supported for amplify-android
# Unit and integration test stack
if LIBRARY == 'amplify':
    code_pipeline_stack_props = {
        # If set, config files for tests will be copied from S3. Otherwise, it will attempt to retrieve using the Amplify CLI
        'config_source_bucket': account_bootstrap.config_source_bucket.bucket_name, 
        'github_source': { 
            'owner': github_owner, 
            'repo': github_repo, 
            'base_branch': branch 
        },
        'device_farm_project_name': 'AmplifyAndroidDeviceFarmTests',
        'codebuild_project_name_prefix': codebuild_project_name_prefix
    }

    pipeline_stack = AmplifyAndroidCodePipeline(app,
                                        f'{stack_name_prefix}AndroidBuildPipeline',
                                        code_pipeline_stack_props,
                                        description="CI Pipeline assets for amplify-android",
                                        env=TARGET_ENV)

# Maven publisher stacks
maven_publisher_stack_props = {
    'github_source': { 
        'owner': github_owner,
        'repo': github_repo, 
        'base_branch': branch,
        'release_pr_branch': release_pr_branch
    },
    'codebuild_project_name_prefix': codebuild_project_name_prefix,
    'create_webhooks': create_webhooks,
    'buildspec_path': maven_deployer_buildspec
}

MavenReleaseStack(app, f'{stack_name_prefix}MavenPublisher', maven_publisher_stack_props, description=f'Assets used for publishing {github_repo} to maven.', env=TARGET_ENV)

app.synth()
