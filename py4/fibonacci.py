import datetime


def fib1(n):
    ''' normal recursion '''
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib1(n - 1) + fib1(n - 2)


known = {0: 0, 1: 1}


def fib2(n):
    ''' recursion with cached results '''
    if n in known:
        return known[n]

    res = fib2(n - 1) + fib2(n - 2)
    known[n] = res
    return res


def fib3(n):
    ''' non-recursion '''
    last1 = 0
    last2 = 1
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n >= 2:
        for _ in range(2, n+1):
            res = last1 + last2
            last1 = last2
            last2 = res
        return last2


def fib4(n):
    ''' use a list to store all the results '''
    l = [0, 1]
    for i in range(2, n+1):
        l.append(l[i-2] + l[i-1])
    return l[n]


if __name__ == '__main__':
    n = 40
    print(datetime.datetime.now())
    print('fib1(%d)=%d' % (n, fib1(n)))
    print(datetime.datetime.now())
    print('fib2(%d)=%d' % (n, fib2(n)))
    print(datetime.datetime.now())
    print('fib3(%d)=%d' % (n, fib3(n)))
    print(datetime.datetime.now())
    print('fib4(%d)=%d' % (n, fib4(n)))
    print(datetime.datetime.now())
