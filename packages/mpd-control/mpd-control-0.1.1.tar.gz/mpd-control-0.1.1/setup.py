#! /usr/bin/env python

from setuptools import setup
from setuptools import find_packages


classifiers = [
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6']

LICENSE = """\
    Copyright (C) 2018  Justin Vermeer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

setup(
    name="mpd-control",
    version='0.1.1',
    license='gpl-3.0',
    description="A Python MPD controller using python-mpd2",
    author="Justin Vermeer",
    author_email="jverm@protonmail.com",
    url="https://github.com/Tazerbot/mpd-control",
    packages=find_packages(),
    py_modules=["python-mpd2"],
    classifiers=classifiers,
    keywords=["mpd"])
