from setuptools import setup, find_packages

setup(
    name="AtCoderStudyBooster",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'atcdr=atcdr.main:main',
        ],
    },
    install_requires=[
        'configparser',
        'requests',
        'beautifulsoup4',
        'colorama',
    ],
    include_package_data=True,
    description="A tool to download and manage AtCoder problems.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="yuta6",
    url="https://github.com/yuta6/AtCoderStudyBooster",
)
