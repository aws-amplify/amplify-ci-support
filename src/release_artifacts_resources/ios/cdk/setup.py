import setuptools

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="cdk",
    version="0.0.1",
    description="Infrastructure code to deploy the AWS resources for release artifacts in Amplify",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "cdk"},
    packages=setuptools.find_packages(where="cdk"),
    install_requires=[
        "aws-cdk.core==1.204.0",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-events",
        "aws-cdk.aws-events-targets",
        "aws-cdk.aws-lambda-python",
        "aws-cdk.aws-cloudfront-origins",
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
