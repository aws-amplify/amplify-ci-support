# Lambda environment variable key, whose value is the
# SecretsManager secret name of the CIrcleCI API key
CIRCLE_CI_IOS_SDK_API_TOKEN_ENV = "CIRCLE_CI_IOS_SDK_API_TOKEN"

# Lambda environment variable key, whose value is the
# SecretsManager secret name of the CIrcleCI API key
CIRCLE_CI_IOS_SDK_SPM_API_TOKEN_ENV = "CIRCLE_CI_IOS_SDK_SPM_API_TOKEN"

# Lambda environment variable key, whose value is the
# ARN of the Lambda execution IAM role
IAM_ROLE_ENV = "IAM_ROLE"

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
RELEASE_BUCKET_NAME_ENV = "SPM_S3_BUCKET_NAME"

# Lambda environment variable key, whose value is the
# CloudFront distribution id that gets invalidated during
# binary artifact releases.
RELEASE_CLOUDFRONT_DISTRIBUTION_ID_ENV = "SPM_RELEASE_CLOUDFRONT_DISTRIBUTION_ID"
