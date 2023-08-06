import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="fnbr-api",
    version="0.0.3",
    author = "Douile",
    description = "Python implementation of the fnbr.co fortnite shop API",
    long_description = read("README"),
    long_description_content_type='text/x-rst',
    license = "MIT",
    keywords = "API fortnite fnbr",
    packages = ["fnbr"],
    install_requires = ["requests"],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License"
    ]
)
