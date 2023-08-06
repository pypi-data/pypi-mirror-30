# -*- coding: utf-8 -*-

"""Console script for which"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import os
import sys
import argparse

sys.path.insert(0, os.getcwd())

from .witch import witch

# Commandline interface
parser = argparse.ArgumentParser()


parser.add_argument("command")

args = parser.parse_args()

kwargs = vars(args)


def main():
    return witch(kwargs["command"])
