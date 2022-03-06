'''
Created on Sep 4, 2014

@author: Jay <smile665@gmail.com>
'''

import socket


def ip_validation(ip):
    '''
    check if the ip address is in a valid format.
    '''
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def connection_validation(ip, port):
    '''
    check if the ip:port can be connected using socket.
    @param port: the port is an integer.
    '''
    if not ip_validation(ip):
        return False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((ip, port))
    if result == 0:
        return True
    else:
        return False


if __name__ == '__main__':
    ip = '192.168.213.11'
    port = 90
    print ip_validation(ip)
    print connection_validation(ip, port)
