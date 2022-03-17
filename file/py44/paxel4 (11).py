#!/usr/bin/env python

'''
Created on May 31, 2014


## okok
@description: use memory_profiler module for profiling programs/functions.
'''

from memory_profiler import profile
from memory_profiler import memory_usage
import time


@profile
def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a


def cur_python_mem():
    mem_usage = memory_usage(-1, interval=0.2, timeout=1)
    return mem_usage


def f(a, n=100):
    time.sleep(1)
    b = [a] * n
    time.sleep(1)
    return b

if __name__ == '__main__':
    a = my_func()
    print cur_python_mem()
    print ""
    print memory_usage((f, (1,), {'n': int(1e6)}), interval=0.5)
