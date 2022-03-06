'''
Created on Oct 14, 2014

@author: Jay <smile665@gmail.com>
'''

import MySQLdb
import ast
import json


def my_run():
    try:
        s = '{"host":"10.1.77.20", "port":3306, "user":"abc",\
              "passwd":"123", "db":"mydb", "connect_timeout":10}'
        d = ast.literal_eval(s)
        print type(d)
        print d
        d1 = eval(s)
        print type(d1)
        print d1
        d2 = json.loads(s)
        print type(d2)
        print d2
        MySQLdb.Connect(host=d['host'], port=d['port'], user=d['user'],
                        passwd=d['passwd'], db=d['db'],
                        connect_timeout=d['connect_timeout'])
        print 'right'
    except Exception, e:
        print 'wrong %s' % e


if __name__ == '__main__':
    my_run()
