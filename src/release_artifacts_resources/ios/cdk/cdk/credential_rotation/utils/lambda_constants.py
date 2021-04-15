# Lambda environment variable key, whose value is the
# SecretsManager secret name of the CIrcleCI API key
CIRCLECI_CONFIG_SECRET_ENV = "CIRCLECI_CONFIG_SECRET"

# Lambda environment variable key, whose value is the
# ARN of the Lambda execution IAM role
CIRCLECI_EXECUTION_ROLE_ENV = "CIRCLECI_EXECUTION_ROLE"

# Lambda environment variable key, whose value is the
# IAM user for whom the rotator will generate static
# credentials
IAM_USERNAME_ENV = "IAM_USERNAME"

# Lambda environment variable key, whose value is the
# GitHub "project path" (e.g., user or org plus project name,
# as in `aws-amplify/aws-sdk-ios`)
GITHUB_PROJECT_PATH_ENV = "GITHUB_PROJECT_PATH"

# Lambda environment variable key, whose value is the
# GitHub username and API token used by CircleCI to
# create PRs in the SPM repo, and merge and tag release
# commits.
GITHUB_CREDENTIALS_SECRET_ENV = "GITHUB_CREDENTIALS_SECRET"

# Lambda environment variable key, whose value is the
# bucket name where release artifacts are uploaded
RELEASE_BUCKET_NAME_ENV = "RELEASE_BUCKET_NAME"

# Lambda environment variable key, whose value is the
# CloudFront distribution id that gets invalidated during
# binary artifact releases.
RELEASE_CLOUDFRONT_DISTRIBUTION_ID_ENV = "RELEASE_CLOUDFRONT_DISTRIBUTION_ID"
