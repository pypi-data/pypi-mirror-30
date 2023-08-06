#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@file:    utils.py
@time:    2018/4/13 15:46
"""
from datetime import datetime


def timeit(func):
    """
    计时装饰器
    """

    def wrapper(*args, **kwargs):
        time_start = datetime.now()
        print(time_start, func.__name__, 'starts...')
        ret = func(*args, **kwargs)
        time_end = datetime.now()
        print(time_end, func.__name__, 'finished.')
        print('Total time used: {!s}'.format(time_end - time_start), '\n')

        return ret

    return wrapper
