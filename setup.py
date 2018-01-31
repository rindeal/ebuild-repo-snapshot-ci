#!/usr/bin/env python3.6

"""
setup.py file for
"""

from distutils.core import setup

import sys
import importlib

from pkgutil import walk_packages
from fnmatch import fnmatch as wc_match
import typing
from itertools import chain


def find_packages(where: typing.Union[str, typing.Sequence[str]], exclude: typing.Optional[typing.Sequence[str]] =None) -> typing.Tuple[str, ...]:
    ret_list: typing.List[str, ...] = []

    if not exclude:
        exclude = ()
    if isinstance(where, str):
        where = (where, )

    exclude: typing.Sequence[str]
    where: typing.Sequence[str]

    for name in chain.from_iterable(map(lambda w: (n for _, n, ispkg in w if ispkg), (walk_packages(p) for p in where))):
        if not any(wc_match(name, p) for p in exclude):
            ret_list.append(name)

    return tuple(ret_list)


setup(
    name="ebuild-repo-snapshot-ci",
    version="0.0.1",
    author="Jan Chren (rindeal)",
    author_email="dev+ebuild-repo-snapshot-ci@janchren.eu",
    description="", # TODO
    license="GPL-3.0",  # https://spdx.org/licenses/GPL-3.0.html
    classifiers=[
        "Development Status :: 3 - Alpha",

        # TODO
        "Topic :: Utilities",
        "Natural Language :: English",

        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",

        "Environment :: Console",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="", # TODO
    packages=find_packages(".", exclude=['*.test*', '*__exclude']),
    # install_requires=[
    #     "posix_ipc",
    #     "cffi",
    # ],
    # python_requires=">=3.6",
    package_data={},
    data_files=[],
    # entry_points={},
)
