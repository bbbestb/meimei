#!/usr/bin/env python


def closure1():
    flist = []

    for i in xrange(3):
        def func(x):
            return x * i
        flist.append(func)

    for f in flist:
        print f(2)


def closure2(msg):
    def printer():
        print msg
    return printer


def not_closure2(msg):
    def printer(msg=msg):
        print msg
    return printer


def generate_power_func(n):
    def nth_power(x):
        return x ** n
    return nth_power


def outer():
    d = {'y': 0}

    def inner():
        d['y'] += 1
        return d['y']
    return inner


def foo():
    a = [1, ]

    def bar():
        a[0] = a[0] + 1
        return a[0]
    return bar


if __name__ == '__main__':
    closure1()
    printer = closure2('Foo!')
    printer()
    printer = not_closure2('Foo!')
    printer()
    raised_to_4 = generate_power_func(4)
    del generate_power_func
    print raised_to_4(2)
    outer = outer()
    print outer()
    foo = foo()
    print foo()
