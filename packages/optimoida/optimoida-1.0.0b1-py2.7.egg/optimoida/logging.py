#!/usr/bin/env python
# coding: utf-8

import huepy

SUCCESS = huepy.blue("SUCCESS")
FAILURE = huepy.red("FAILURE")


class Logger(object):

    def info(self, msg, flag=None):

        if flag:
            return huepy.run("{0} {1}".format(flag, msg))

        else:
            return huepy.run(msg)

    def warn(self, msg):

        return huepy.info(msg)

    def error(self, msg, flag=None):

        if flag:
            return huepy.bad("{0} {1}".format(flag, msg))

        else:
            return huepy.bad(msg)


logger = Logger()
