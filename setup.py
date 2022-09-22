"""Setup file."""

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), encoding="utf8") as fp:
        return fp.read()


setup(
    name="languagetool",
    version="0.0.1",
    author="Martin Schmitt",
    author_email="martin.schmitt@celebrate.company",
    description=("A wrapper around the LanguageTool API (languagetool.org))"),
    license="MIT",
    keywords="language grammar wrapper dictionary",
    # url="http://packages.python.org/an_example_pypi_project",
    packages=["languagetool"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=["requests"],
)
