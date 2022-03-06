#!/usr/bin/env python
# _*_ coding:utf-8 _*_

from multiprocessing import Process, Queue
import time
import random


# 写数据进程执行的代码:
def write(q):
    for value in ['A', 'B', 'C']:
        print 'Put %s to queue...' % value
        q.put(value)
        time.sleep(random.random())


# 读数据进程执行的代码:
def read(q):
    while True:
        value = q.get(True)
        print 'Get %s from queue.' % value


if __name__ == '__main__':
    # 父进程创建Queue，并传给各个子进程：
    queue = Queue()
    p_write = Process(target=write, args=(queue,))
    p_read = Process(target=read, args=(queue,))
    # 启动子进程pw，写入:
    p_write.start()
    # 启动子进程pr，读取:
    p_read.start()
    # 等待pw结束:
    p_write.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止:
    p_read.terminate()
