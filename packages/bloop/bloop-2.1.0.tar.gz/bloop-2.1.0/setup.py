import os
import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
README = (HERE / "README.rst").read_text()
CHANGES = (HERE / "CHANGELOG.rst").read_text()
VERSION = "VERSION-NOT-FOUND"
for line in (HERE / "bloop" / "__init__.py").read_text().split("\n"):
    if line.startswith("__version__"):
        VERSION = eval(line.split("=")[-1])

REQUIREMENTS = [
    "blinker==1.4",
    "boto3>=1.7.1,<=1.8.0",
    "botocore>=1.10.1"  # no upper bound because we'll take what boto3 uses
]

if __name__ == "__main__":
    setup(
        name="bloop",
        version=VERSION,
        description="ORM for DynamoDB",
        long_description=README + "\n\n" + CHANGES,
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Topic :: Software Development :: Libraries"
        ],
        author="Joe Cross",
        author_email="joe.mcross@gmail.com",
        url="https://github.com/numberoverzero/bloop",
        license="MIT",
        keywords="aws dynamo dynamodb dynamodbstreams orm",
        platforms="any",
        include_package_data=True,
        packages=find_packages(exclude=("docs", "examples", "scripts", "tests")),
        install_requires=REQUIREMENTS,
    )
