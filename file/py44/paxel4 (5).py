import urllib2

url = 'http://192.168.211.23:8080/status'
#url = 'http://192.168.213.142:8080/check/status'
#url = 'hhhp://192.168.213.142:8080/check/status'
req = urllib2.Request(url)
try:
    resp = urllib2.urlopen(req, timeout=5)
except urllib2.HTTPError, e:
    if e.code == 404:
        print 'response code 404'
    else:
        print 'not 404. response code %d' % e.code
except urllib2.URLError, e:
    print 'URLError %s' % e.reason
else:
    # 200
    print 'http code 200'
    body = resp.read()
    print body
