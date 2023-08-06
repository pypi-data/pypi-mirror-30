#!/usr/bin/env python
# coding: utf-8

import os

from configparser import ConfigParser

DEFAULT_CONFIG_FILE = os.path.abspath(
    os.path.join(os.environ["HOME"], ".optimoida.ini")
)


def get_api_key(config_file=DEFAULT_CONFIG_FILE):

    if not os.path.isfile(config_file):
        raise IOError("~/.optimoida.ini doesn't found.")

    parser = ConfigParser()
    parser.read(config_file)

    return parser.get("tinypng", "key")
