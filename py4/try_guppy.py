#!/usr/bin/env python

'''
Created on May 31, 2014

@author: Jay <smile665@gmail.com>

@description: just try to use Guppy-PE (useing Heapy) for memory profiling.
'''


from guppy import hpy

a = [8] * (10 ** 6)

h = hpy()
print h.heap()
print h.heap().more
print h.heap().more.more
