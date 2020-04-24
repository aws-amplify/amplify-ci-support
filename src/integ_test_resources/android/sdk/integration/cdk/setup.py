import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="cdk_integration_tests_android",
    version="0.0.1",

    description="Android SDK integration tests resource manager",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "cdk_integration_tests_android"},
    packages=setuptools.find_packages(where="cdk_integration_tests_android"),

    install_requires=[
        "aws-cdk.core==1.34.1",
        "aws-cdk.aws-pinpoint",
        "aws-cdk.aws_cognito",
        "aws-cdk.aws_iam",
        "aws-cdk.aws_s3"
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
