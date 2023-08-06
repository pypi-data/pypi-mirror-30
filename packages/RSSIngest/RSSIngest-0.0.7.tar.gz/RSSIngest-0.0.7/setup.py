"""
Module for ingesting news articles from various sources' RSS feeds.
"""

from sys import prefix
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="RSSIngest",
    version="0.0.7",
    description="Module for ingesting news articles from various sources' RSS feeds.",
    long_description=long_description,
    author="Ash Prince",
    author_email="i7629228@bournemouth.ac.uk",
    packages=find_packages(),
    install_requires=["pymongo", 'nltk', 'beautifulsoup4', 'PyYAML', 'feedparser'],
    scripts=["RSSIngest/bin/article_interpreter", "RSSIngest/bin/rss_ingest"],
    include_package_data=True,
    package_data={"outlets": [path.join(here, "RSSIngest/config/config.yaml")]}
)
