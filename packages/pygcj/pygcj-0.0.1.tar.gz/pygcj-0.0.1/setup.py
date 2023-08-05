#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
from datetime import date
from setuptools import setup, find_packages

import pygcj as package

if __name__ == "__main__":
    PKG_NAME = package.__name__

    GITHUB_USERNAME = package.__github_username__
    
    SHORT_DESCRIPTION = package.__short_description__
    
    LONG_DESCRIPTION = open("README.rst", "rb").read().decode("utf-8")
    
    VERSION = package.__version__

    AUTHOR = package.__author__

    AUTHOR_EMAIL = package.__author_email__
    
    MAINTAINER = package.__maintainer__
    
    MAINTAINER_EMAIL = package.__maintainer_email__
    
    PACKAGES, INCLUDE_PACKAGE_DATA, PACKAGE_DATA, PY_MODULES = (
        None, None, None, None,
    )

    if os.path.exists(__file__[:-8] + PKG_NAME):
        PACKAGES=[PKG_NAME] + ["%s.%s" % (PKG_NAME, i)
                               for i in find_packages(PKG_NAME)]
    
        INCLUDE_PACKAGE_DATA = True
        PACKAGE_DATA = {
            "pygcj":["gcps_gd"],
        }
    elif os.path.exists(__file__[:-8] + PKG_NAME + ".py"):
        PY_MODULES = [PKG_NAME, ]

    repository_name = os.path.basename(os.path.dirname(__file__))

    URL = "https://github.com/{0}/{1}".format(GITHUB_USERNAME, repository_name)
    # Use todays date as GitHub release tag
    github_release_tag = str(date.today())
    # Source code download url
    DOWNLOAD_URL = "https://github.com/{0}/{1}/tarball/{2}".format(
        GITHUB_USERNAME, repository_name, github_release_tag)
    
    LICENSE = package.__license__

    PLATFORMS = [
        "Windows",
        "MacOS",
        "Unix",
    ]
    
    

    REQUIRES = list()
    f = open("requirements.txt", "rb")
    for line in f.read().decode("utf-8").split("\n"):
        line = line.strip()
        if "#" in line:
            line = line[:line.find("#")].strip()
        if line:
            REQUIRES.append(line)

    setup(
        name=PKG_NAME,
        description=SHORT_DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        packages=PACKAGES,
        include_package_data=INCLUDE_PACKAGE_DATA,
        package_data=PACKAGE_DATA,
        py_modules=PY_MODULES,
        url=URL,
        download_url=DOWNLOAD_URL,
        platforms=PLATFORMS,
        license=LICENSE,
        install_requires=REQUIRES,
    )

