import setuptools

setuptools.setup(
    name="cdk_integration_tests_ios",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description="TODO: Fill",
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "cdk_integration_tests_ios"},
    packages=setuptools.find_packages(where="cdk_integration_tests_ios"),

    install_requires=[
        "aws-cdk.core==1.34.1",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-apigateway",
        "aws-cdk.aws-cloudformation",
        "aws-cdk.aws-cognito",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-ssm",
        "aws-cdk.aws-pinpoint"
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
