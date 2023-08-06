import os
import subprocess
import sys

from setuptools import find_packages, setup


def version():
    with open("homophone/__init__.py") as fh:
        for line in fh.readlines():
            if line.startswith("__version__"):
                vsn = line.split("=")[1].replace('"', "").strip()
                break
    if "dev" in vsn:
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"])
        git_hash = git_hash.decode()[:7]
        git_vsn = ["git"]
        try:
            try:
                null = subprocess.DEVNULL
            except AttributeError:
                null = open(os.devnull, "w")
            delta = subprocess.check_output(["git", "describe"], stderr=null)
        except subprocess.CalledProcessError:
            pass
        else:
            git_vsn.append(delta.decode().split("-")[1])
        git_vsn.append(git_hash)
        vsn += "+" + ".".join(git_vsn)
    return vsn

VERSION = version()


def author():
    with open("homophone/__init__.py") as fh:
        for line in fh.readlines():
            if line.startswith("__author__"):
                name, email = line.rsplit(" ", 1)
                break
    name = name.split("=")[1].strip().replace('"', "")
    email = email.strip().replace("<", "").replace(">", "").replace('"', "")
    return name, email

AUTHOR_NAME, AUTHOR_EMAIL = author()


SHORT_DESCRIPTION = "Discover music"


def long_description():
    try:
        open("README.md").read()
    except IOError:
        return SHORT_DESCRIPTION

LONG_DESCRIPTION = long_description()

def development_status():
    tmpl = "Development Status :: {code:d} - {status}"
    if "dev" in VERSION:
        code, status = 2, "Pre-Alpha"
    elif "a" in VERSION:
        code, status = 3, "Alpha"
    elif "b" in VERSION:
        code, status = 4, "Beta"
    elif "rc" in VERSION:
        code, status = 4, "Beta"
    else:
        code, status = 5, "Production/Stable"
    return tmpl.format(code=code, status=status)

DEVELOPMENT_STATUS = development_status()


setup(
    name="homophone",
    version=VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/mdippery/homophone.py",
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "click",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "homophone=homophone.__main__:main",
        ]
    },
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "funcsigs",
        "pytest",
        "pytest-cov",
        "tox",
        "vcrpy",
    ],
    classifiers=[
        DEVELOPMENT_STATUS,
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
