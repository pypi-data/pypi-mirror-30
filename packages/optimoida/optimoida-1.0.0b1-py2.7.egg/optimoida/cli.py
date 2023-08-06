#!/usr/bin/env python
# coding: utf-8

from argparse import (
    ArgumentParser,
    ZERO_OR_MORE
)

parser = ArgumentParser(
    prog="optimoida",
    description="Optimize the image file by TinyPNG API."
)

parser.add_argument(
    "path",
    action="store",
    metavar="PATH",
    nargs=ZERO_OR_MORE,
    help="The image file or directory path.")

parser.add_argument(
    "--dev",
    action="store_true",
    help="Run optimoida with development mode.")
