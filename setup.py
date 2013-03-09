from distutils.core import setup

setup(
    name = "setix",
    packages = ["setix", "setix.backends"],
    version = "0.8",
    description = "Fast data structures for finding intersecting sets and similar strings",
    author = "Marcin Pertek",
    author_email = "kat.zygfryd@gmail.com",
    url = "http://github.com/zygfryd/setix",
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
    requires = ["numpy (>=1.5.0)", "six"],
    long_description = """\
"""
)
