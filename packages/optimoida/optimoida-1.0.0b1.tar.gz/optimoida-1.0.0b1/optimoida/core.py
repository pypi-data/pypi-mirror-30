#!/usr/bin/env python
# coding: utf-8

import os
import tinify

from yaspin import yaspin
from tinify import (
    ClientError, ServerError, ConnectionError)

from optimoida.config import get_api_key
from optimoida.logging import (
    SUCCESS, FAILURE, logger)

IMAGE_EXTS = [".jpg", ".JPG", ".png", ".PNG"]


def check_extension(path):

    result = os.path.splitext(path)[-1]

    if result in IMAGE_EXTS:
        return True

    else:
        raise IOError("This file is not a image file: '{0}'".format(path))


def _optimize_file(path):

    tinify.key = get_api_key()
    log_msg = "optimized: {0}".format(path)

    with yaspin(text="Optimizing", color="cyan") as spinner:

        try:
            source = tinify.from_file(path)
            source.to_file(path)

            log = logger.info(log_msg, flag=SUCCESS)

        except (ClientError, ServerError, ConnectionError):
            log = logger.error(log_msg, flag=FAILURE)

        finally:
            spinner.write(log)


def _optimize_dir(path):

    for current, dirs, files in os.walk(path):

        if current.find("git") != -1:
            continue

        absfiles = map((lambda f: os.path.join(current, f)), files)

        for _file in absfiles:

            try:
                check_extension(_file)
                _optimize_file(_file)

            except IOError:
                print logger.warn(
                    "This is not image file: '{0}'".format(_file))


def optimize(paths):

    for path in paths:

        if os.path.isfile(path):

            check_extension(path)
            _optimize_file(path)

        elif os.path.isdir(path):

            _optimize_dir(path)
