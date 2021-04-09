# Lambda environment variable for the key that holds
# SecretsManager CircleCI api key
CIRCLECI_CONFIG_SECRET_ENV = "CIRCLECI_CONFIG_SECRET"

# Lambda environment variable for the key that holds
# the lambda execution role arn
CIRCLECI_EXECUTION_ROLE_ENV = "CIRCLECI_EXECUTION_ROLE"

# Lambda environment variable for the key that holds
# the user name the lambda requires to get credentions
IAM_USERNAME_ENV = "IAM_USERNAME"

# Lambda environment variable for the key that holds
# the github path for the project
GITHUB_PROJECT_PATH_ENV = "GITHUB_PROJECT_PATH"

# Lambda environment variable for the key that holds
# SecretsManager GitHub credentials.
GITHUB_CREDENTIALS_SECRET_ENV = "GITHUB_CREDENTIALS_SECRET"

# Lambda environment variable for the key that holds
# bucket name where release artifacts are uploaded
RELEASE_BUCKET_NAME_ENV = "RELEASE_BUCKET_NAME"

# Lambda environment variable for the key that holds
# cloudfront distribution id
RELEASE_CLOUDFRONT_DISTRIBUTION_ID_ENV = "RELEASE_CLOUDFRONT_DISTRIBUTION_ID"
