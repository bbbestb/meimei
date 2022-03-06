#!/usr/bin/env python
#coding=utf-8
# FROM: http://blog.sina.com.cn/s/blog_4ef8be9f0100fe67.html

import os
import sys
import time
import urllib
import urllib2
import threading

#############################################################################
#
# self-defined exception classes
#
#############################################################################
class ConnectionError(Exception): pass
class URLUnreachable(Exception):pass
class CanotDownload(Exception):pass

#############################################################################
#
# multiple threads download module starts here
#
#############################################################################
class HttpGetThread(threading.Thread):
    def __init__(self, name, url, filename, range=0):
        threading.Thread.__init__(self, )
        self.url = url
        self.filename = filename
        self.range = range
        self.totalLength = range[1] - range[0] +1
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0
        self.percent = self.downloaded/float(self.totalLength)*100
        self.headerrange = (self.range[0]+self.downloaded, self.range[1])
        self.bufferSize = 8192


    def run(self):
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0
        self.percent = self.downloaded/float(self.totalLength)*100
        #self.headerrange = (self.range[0]+self.downloaded, self.range[1])
        self.bufferSize = 8192
        #request = urllib2.Request(self.url)
        #request.add_header('Range', 'bytes=%d-%d' %self.headerrange)
        downloadAll = False
        retries = 1
        while not downloadAll:
            if retries > 10:
                break
            try:
                self.headerrange = (self.range[0]+self.downloaded, self.range[1])
                request = urllib2.Request(self.url)
                request.add_header('Range', 'bytes=%d-%d' %self.headerrange)
                conn = urllib2.urlopen(request)
                startTime = time.time()
                data = conn.read(self.bufferSize)
                while data:
                    f = open(self.filename, 'ab')
                    f.write(data)
                    f.close()
                    self.time = int(time.time() - startTime)
                    self.downloaded += len(data)
                    self.percent = self.downloaded/float(self.totalLength) *100
                    data = conn.read(self.bufferSize)
                downloadAll = True
            except Exception, err:
                retries += 1
                time.sleep(1)
                continue

def Split(size,blocks):
    ranges = []
    blocksize = size / blocks
    for i in xrange(blocks-1):
        ranges.append(( i*blocksize, i*blocksize+blocksize-1))
    ranges.append(( blocksize*(blocks-1), size-1))

    return ranges

def GetHttpFileSize(url):
    length = 0
    try:
        conn = urllib.urlopen(url)
        headers = conn.info().headers
        for header in headers:
            if header.find('Length') != -1:
                length = header.split(':')[-1].strip()
                length = int(length)
    except Exception, err:
        pass

    return length

def hasLive(ts):
    for t in ts:
        if t.isAlive():
            return True
    return False

def MyHttpGet(url, output=None, connections=4):
    """
    arguments:
        url, in GBK encoding
        output, default encoding, do no convertion
        connections, integer
    """
    length = GetHttpFileSize(url)
    print length
    mb = length/1024/1024.0
    if length == 0:
        raise URLUnreachable
    blocks = connections
    if output:
        filename = output
    else:
        output = url.split('/')[-1]
    ranges = Split(length, blocks)
    names = ["%s_%d" %(output,i) for i in xrange(blocks)]

    ts = []
    for i in xrange(blocks):
        t = HttpGetThread(i, url, names[i], ranges[i])
        t.setDaemon(True)
        t.start()
        ts.append(t)

    live = hasLive(ts)
    startSize = sum([t.downloaded for t in ts])
    startTime = time.time()
    etime = 0
    while live:
        try:
            etime = time.time() - startTime
            d = sum([t.downloaded for t in ts])/float(length)*100
            downloadedThistime = sum([t.downloaded for t in ts])-startSize
            try:
                rate = downloadedThistime / float(etime)/1024
            except:
                rate = 100.0
            progressStr = u'\rFilesize: %d(%.2fM) Downloaded: %.2f%% Avg rate: %.1fKB/s' %(length, mb, d, rate)
            sys.stdout.write(progressStr)
            sys.stdout.flush()
            #sys.stdout.write('\b'*(len(progressStr)+1))
            live = hasLive(ts)
            time.sleep(0.2)
        except KeyboardInterrupt:
            print
            print "Exit..."
            for n in names:
                try:
                    os.remove(n)
                except:
                    pass
            sys.exit(1)

    print
    #print u'used time： %d:%d, pingjunsudu：%.2fKB/s' %(int(etime)/60, int(etime)%60,rate)

    f = open(filename, 'wb')
    for n in names:
        f.write(open(n,'rb').read())
        try:
            os.remove(n)
        except:
            pass
    f.close()


if __name__ == '__main__':
    MyHttpGet('http://dldir1.qq.com/qqfile/QQforMac/QQ_V3.1.1.dmg','my_download.file',4)
