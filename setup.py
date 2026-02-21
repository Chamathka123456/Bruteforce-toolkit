from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Bruteforce-toolkit",
    version="1.0.0",
    author="Your Name",
    description="Educational password testing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/password-guesser",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.28.0",
        "colorama>=0.4.6",
        "fake-useragent>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "password-guesser=guesser:main",
        ],
    },
)
