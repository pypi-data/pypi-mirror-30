#!/usr/bin/env python
# coding: utf-8

import sys
import traceback

from optimoida.cli import parser
from optimoida.core import optimize


def main():

    if len(sys.argv) == 1:
        parser.parse_args(["-h"])
        sys.exit(0)

    args = parser.parse_args()
    print args

    try:
        return_code = optimize(args.path)
        sys.exit(return_code)

    except Exception as e:
        stack_trace = traceback.format_exc()

        if args.dev:
            error_msg = stack_trace

        else:
            error_msg = "{0}: {1}\n".format(type(e).__name__, e.message)

        sys.stderr.write(error_msg)


if __name__ == '__main__':

    main()
