#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for twitter_mood.

    This file was generated with PyScaffold 3.0.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: http://pyscaffold.org/
"""

import sys
from setuptools import setup

# Add here console scripts and other entry points in ini-style format
entry_points = """
[console_scripts]
# script_name = twitter_mood.module:function
# For example:
# fibonacci = twitter_mood.skeleton:run
"""

requires = ['pyscaffold>=3.0a0,<3.1a0',
            'textblob>=0.15.1,<0.16.0',
            ]


def setup_package():
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    sphinx = ['sphinx'] if needs_sphinx else []
    setup(setup_requires=requires + sphinx,
          entry_points=entry_points,
          use_pyscaffold=True)


if __name__ == "__main__":
    setup_package()
