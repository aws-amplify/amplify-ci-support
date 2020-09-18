import setuptools

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="amplify_integration_tests_android",
    version="0.0.1",
    description="Amplify integration tests resource manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    packages=setuptools.find_packages(where="."),
    install_requires=[
        "aws-cdk.core==1.34.1",
        "aws-cdk.aws_codebuild",
        "aws_cdk.aws_logs",
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
