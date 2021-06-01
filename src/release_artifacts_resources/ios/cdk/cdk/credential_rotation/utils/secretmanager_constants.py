# Secrets Manager secret name, whose value is the
# CircleCI API key used by the Lambda credential rotator
# to update environment variables for aws ios sdk repo.
CIRCLECI_AWS_IOS_SDK_API_KEY = "CIRCLECI_AWS_IOS_SDK_API_KEY"

# Secrets Manager secret name, whose value is the
# CircleCI API key used by the Lambda credential rotator
# to update environment variables for aws ios sdk spm repo.
CIRCLECI_AWS_IOS_SDK_SPM_API_KEY = "CIRCLECI_AWS_IOS_SDK_SPM_API_KEY"

# Secrets Manager secret name, whose value is a
# JSON containing the GitHub API token for updating
# the Swift Package Manager manifest repo, and the
# GitHub username that owns that API token.
GITHUB_SPM_RELEASE_API_TOKEN = "GITHUB_SPM_RELEASE_API_TOKEN"
