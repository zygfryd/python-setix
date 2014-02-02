import os

from distutils.core import setup

setup(
    name = "setix",
    packages = ["setix", "setix.backends"],
    version = "0.8.2",
    description = "Fast data structures for finding intersecting sets and similar strings",
    author = "Marcin Pertek",
    author_email = "kat.zygfryd@gmail.com",
    license = "MIT",
    url = "http://github.com/zygfryd/python-setix",
    keywords = ["set", "intersection", "index", "trgm", "fuzzy"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    install_requires = ["numpy>=1.5.0", "six"],
    long_description = open(os.path.join(os.path.dirname(__file__), "README.rst"), "rb").read ()
)
