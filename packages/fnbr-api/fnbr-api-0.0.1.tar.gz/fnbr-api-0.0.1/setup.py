import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="fnbr-api",
    version="0.0.1",
    author = "Douile",
    description = "Easy use of the fnbr.co api",
    license = "Apache",
    keywords = "API fortnite fnbr",
    packages = ["fnbr"],
    install_requires = ["requests"]
)
