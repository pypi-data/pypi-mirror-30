#!/usr/bin/env python
import os
import sys

__all__ = ["STDIN"]


def read_stdin():
    if os.fstat(sys.stdin.fileno()).st_size > 0:
        return sys.stdin.read()


STDIN = read_stdin()
