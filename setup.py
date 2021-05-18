#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="tap-nikabot",
    version="1.0.8",
    description="Singer.io tap for extracting data from Nikabot",
    python_requires=">=3.6.0",
    author="Paul Heasley",
    author_email="paul@phdesign.com.au",
    url="https://github.com/singer-io/tap-nikabot",
    keywords=["nikabot", "singer", "stitch", "tap"],
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_nikabot"],
    install_requires=["singer-python==5.9.0", "requests==2.23.0", "backoff==1.8.0"],
    extras_require={
        "dev": [
            "black==19.10b0",
            "coverage==5.1",
            "ipdb==0.13.7",
            "isort==4.3.21",
            "mypy==0.780",
            "pylint==2.7.2",
            "pytest-socket==0.3.5",
            "pytest==5.4.3",
            "requests-mock==1.8.0",
        ]
    },
    entry_points="""
    [console_scripts]
    tap-nikabot=tap_nikabot:main
    """,
    packages=find_packages(exclude=("tests",)),
    package_data={"schemas": ["tap_nikabot/schemas/*.json"]},
    include_package_data=True,
)
