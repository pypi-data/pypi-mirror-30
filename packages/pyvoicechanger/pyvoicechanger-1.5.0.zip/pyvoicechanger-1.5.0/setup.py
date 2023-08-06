#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# To generate DEB package from Python Package:
# sudo pip3 install stdeb
# python3 setup.py --verbose --command-packages=stdeb.command bdist_deb
#
#
# To generate RPM package from Python Package:
# sudo apt-get install rpm
# python3 setup.py bdist_rpm --verbose --fix-python --binary-only
#
#
# To generate EXE MS Windows from Python Package (from MS Windows only):
# python3 setup.py bdist_wininst --verbose
#
#
# To generate PKGBUILD ArchLinux from Python Package (from PyPI only):
# sudo pip3 install git+https://github.com/bluepeppers/pip2arch.git
# pip2arch.py PackageNameHere
#
#
# To Upload to PyPI by executing:
# sudo pip install --upgrade pip setuptools wheel virtualenv
# python3 setup.py bdist_egg bdist_wheel --universal sdist --formats=zip upload --sign


"""Setup.py for Python, as Generic as possible."""


import re

from pathlib import Path

from setuptools import setup


SOURCE = (Path(__file__).parent / "pyvoicechanger.py").read_text()


##############################################################################
# Dont touch below


def find_this(search, source=SOURCE):
    """Take a string and a filename path string and return the found value."""
    print("Searching for {what}.".format(what=search))
    if not search or not source:
        print("Not found on source: {what}.".format(what=search))
        return ""
    return str(re.compile(r".*__{what}__ = '(.*?)'".format(
        what=search), re.S).match(source).group(1)).strip().replace("'", "")


##############################################################################


setup(

    name="pyvoicechanger",
    version=find_this("version"),

    description="Real Time Microphone Voice Changer.",
    long_description="PyVoiceChanger is a Real Time Microphone Voice Changer App.",

    url=find_this("url"),
    license=find_this("license"),

    author=find_this("author"),
    author_email=find_this("email"),
    maintainer=find_this("author"),
    maintainer_email=find_this("email"),

    include_package_data=True,
    zip_safe=True,

    python_requires='>=3.6',

    tests_require=['isort', 'prospector', 'pre-commit', 'pre-commit-hooks'],

    keywords=['voice', 'changer', 'utils', 'real time', 'utility'],

    scripts=["pyvoicechanger.py"],

    classifiers=[

        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Other Audience',

        'Natural Language :: English',

        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
