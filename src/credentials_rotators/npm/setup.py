import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="npm",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "npm"},
    packages=setuptools.find_packages(where="npm"),

    install_requires=[
        "aws-cdk.core>=1.74.0",
        "aws_cdk.aws_lambda",
        "aws_cdk.aws_secretsmanager",
        "aws_cdk.aws_iam",
        "aws_cdk.aws_sns",
        "aws_cdk.aws_sns_subscriptions",
        "aws_cdk.aws_cloudwatch_actions",
        "boto3"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
