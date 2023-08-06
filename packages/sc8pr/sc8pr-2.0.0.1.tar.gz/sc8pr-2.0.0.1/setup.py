from setuptools import setup, find_packages

with open("README.txt") as f: readme = f.read()

setup(
    # Package info
    name = "sc8pr",
    version = "2.0.0.1",
    license = "GPLv3",
    packages = find_packages(),
    package_data = {"sc8pr": ["*.data", "examples/img/*.*"]},

    # Author
    author = "David MacCarthy",
    author_email = "sc8pr.py@gmail.com",

    # Dependencies
    python_requires = ">=3.4, <4",
    install_requires = ["pygame(>=1.9.1)"],
    
    # URLs
    url = "http://dmaccarthy.github.io/sc8pr",
    download_url = "https://github.com/dmaccarthy/sc8pr/archive/v2.0.0.zip",

    # Details
    description = "A simple framework for new and experienced Python programmers to create animations, games, robotics simulations, and other graphics-based programs",
    long_description = readme,

    # Additional data
    keywords = "graphics animation sprite gui robotics pygame educational",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Education",
        "Framework :: Robot Framework :: Library"
    ]
)
