from setuptools import find_packages, setup


def parse_requirements(filename):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="AtCoderStudyBooster",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "atcdr=atcdr.main:main",
        ],
    },
    install_requires=parse_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "black",
            "isort",
            "flake8",
            "mypy",
            "pre-commit",
            "pytest",
        ],
    },
    include_package_data=True,
    description="A tool to download and manage AtCoder problems.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="yuta6",
    url="https://github.com/yuta6/AtCoderStudyBooster",
)
