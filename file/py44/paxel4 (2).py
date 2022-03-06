# -*- coding: utf-8 -*-

'''
Created on Apr 18, 2014

@author: Jay <yongjie.ren@dianping.com>
'''

import sys
sys.path.append("..")
import lib.file2list as file2list
import lib.db_connection as db_connection
from config import dianping_db_config
import random
import urllib
import json
import os
from xml.dom import minidom
import codecs 


class poi(object):
    '''
    POI class for the QA dashboard.
    '''
    
    poi_xml = 'poi.xml'
    poi_with_search_xml = 'poi_with_search.xml'
    
    def __init__(self, cityfile='cities.txt', shoptype='10', sample_cnt=10, searcher_host='192.168.5.149:4053'):
        '''
        Constructor:
        cityfile='cities.txt' # for city list file
        shoptype='10'  # for '美食' category
        sample_cnt=10  # how many samples will be collected
        searcher_host  # the host and port of the shop search engine 
            QA env: searcher_host='192.168.5.149:4053'
            Product env: searcher_host='10.1.1.158:4053'
        '''
        
        self.myfile = cityfile
        self.shoptype = shoptype
        self.sample_cnt = sample_cnt
        self.city_list = file2list.list_from_file(cityfile)
#        self.city_list = ['长沙']   #just for debugging
        self.searcher_host = searcher_host
    
    def get_poi_info(self):
        '''
        get random POI samples from the initiated city list.
        '''
        
        poi_info_list = []
        cnx = db_connection.connect_db(**dianping_db_config)
        if cnx == None:
            print "DianPing DB connection ERROR!!"
            sys.exit(1)
        cursor = cnx.cursor()
        for city in self.city_list:
            sql1 = "SELECT shop.ShopID FROM ZS_CityList as cl, DP_Shop as shop WHERE cl.CityID=shop.CityID AND ShopType='%s' " % self.shoptype \
                 + "AND cl.CityName='%s' AND shop.GLat is not null AND shop.Glng is not null AND shop.Glat!=0 AND shop.Glng!=0 " % city \
                 + "AND (shop.Power IN(0, 2, 3, 4, 5, 10) OR (shop.Power=1 AND shop.LastDate >= '2013-07-01' )) " \
                 + "AND shop.shopid NOT IN (SELECT ShopID FROM DP_ClosedShop)" \
                 + "AND shop.ShopID NOT IN (SELECT ShopID FROM DP_ShopAutoAudit WHERE STATUS<>2);" 
            cursor.execute(sql1)
            rows = cursor.fetchall()
#            print rows.__sizeof__()
            if len(rows) >= self.sample_cnt:
                shopid_list = [row[0] for row in rows]
                new_shopid_list = random.sample(shopid_list, self.sample_cnt)
#                print new_shopid_list
#                print shopid_list.__sizeof__()
            for id in new_shopid_list:
                temp_list = []
                sql2 = "SELECT shop.ShopID, shop.ShopName, shop.GLng, shop.GLat, cl.CityID, cl.CityName FROM ZS_CityList as cl, DP_Shop as shop "\
                     + "WHERE cl.CityID=shop.CityID AND shop.ShopID='%s' LIMIT 1;"  % str(id)
                cursor.execute(sql2)
                rows = cursor.fetchone()
                for i in rows:
                    temp_list.append(i)
                poi_info_list.append(temp_list)
        return poi_info_list
    
    def poi_info_to_xml(self, poi_info_list=None):
        '''
        save poi_info_list to a XML file.
        '''
        
        impl = minidom.getDOMImplementation()  
        dom = impl.createDocument(None, 'poi', None)  
        root = dom.documentElement
        
        for i in poi_info_list:
            shop = dom.createElement('shop')
            shop.setAttribute('id', str(i[0]) )
            shopname = dom.createElement('shopname')
            shopname_text = dom.createTextNode(i[1])
            shopname.appendChild(shopname_text)
            lng = dom.createElement('longitude')
            lng_text = dom.createTextNode(str(i[2]))
            lng.appendChild(lng_text)
            lat = dom.createElement('latitude')
            lat_text = dom.createTextNode(str(i[3]))
            lat.appendChild(lat_text)
            cityid = dom.createElement('cityid')
            cityid_text = dom.createTextNode(str(i[4]))
            cityid.appendChild(cityid_text)
            cityname = dom.createElement('cityname')
            cityname_text = dom.createTextNode(i[5])
            cityname.appendChild(cityname_text)
            imgname = dom.createElement('imgname')
            imgname_text = dom.createTextNode('%s_%s.jpg' % (i[4], i[0]))
            imgname.appendChild(imgname_text)
            
            shop.appendChild(shopname)
            shop.appendChild(lng)
            shop.appendChild(lat)
            shop.appendChild(cityid)
            shop.appendChild(cityname)
            shop.appendChild(imgname)
             
            root.appendChild(shop)
            
        f = codecs.open(self.poi_xml, 'w', 'utf-8')  
        dom.writexml(f, addindent='  ', newl='\n')  
        f.close()
    
    def xml_to_poi_info_list (self):
        '''
        load xml to a poi_info_list.
        '''
        
        poi_info_list = []
        xmldoc = minidom.parse(self.poi_xml)
        shops = xmldoc.getElementsByTagName('shop')
        for shop in shops:
            shopid = shop.getAttribute('id')
            shopname = shop.getElementsByTagName('shopname')[0].childNodes[0].nodeValue
            lng = shop.getElementsByTagName('longitude')[0].childNodes[0].nodeValue
            lat = shop.getElementsByTagName('latitude')[0].childNodes[0].nodeValue
            cityid = shop.getElementsByTagName('cityid')[0].childNodes[0].nodeValue
            cityname = shop.getElementsByTagName('cityname')[0].childNodes[0].nodeValue
            poi_info_list.append([shopid, shopname, lng, lat, cityid, cityname])
        return poi_info_list
                    
    def get_search_info(self, poi_info=None):
        '''
        poi_info must be a list as [shopid, shopname, longitude, latitude, citiyid, cityname]
            e.g. [9125655, '龙马川菜馆', 119.940181, 31.969895, 93, '常州']
        '''
        
        searcher_host = self.searcher_host
        tmpfile = 's.out'
        distant = 1000  # 1000m nearby
        query_url = "http://%s/search/shop?query=term(categoryids,10),geo(poi,%s:%s,%s)&sort=desc(dpscore)&" % (searcher_host, poi_info[2], poi_info[3], distant) \
                  + "fl=dist(poi,%s:%s),shopid,shopname,shoppower,branchname,altname,power," % (poi_info[2], poi_info[3]) \
                  + "shopgroupid,shoptype,cityid,defaultpic,avgprice,hasgroupuid,address,crossroad,score1,score2,score2,dishtags,pictotal,hasbooksetting,"\
                  + "dealgroupid,membercardid,votetotal,hasmembercard,booktype,dealgrouptitle,dealgroupprice,contenttitle,hasticket,region1,"\
                  + "category1,gpoi,isnewshop,shoptags,publictransit,haspromo,prepaidcards,hastakeaway,hasshortdeals,marketprice,poi,"\
                  + "mopaystatus&limit=0,25&info=clientversion:6.5,app:PointShopSearch,platform:MAPI," \
                  + "referrequestid:013d92a7-a7eb-45b9-8534-5ccd0c176b1a,"\
                  + "useragent:MApi+1.1+%%28com.dianping.v1+6.5+om_sd_xiaomishichang+MI_3W%%3B+Android+4.3%%29,userlng:121.41542,"\
                  + "queryid:f1efe724-9fb4-4e50-954a-e700f3c5e5a5,clientip:192.168.213.52,userlat:31.21746,sorttype:1,"\
                  + "unrelatedguidefields:categoryids%%3Bregionids,geoFieldName:poi,mobileplatform:1,poi:%s%%A%s," % (poi_info[2], poi_info[3]) \
                  + "wifi:,dpid:-7517157582792622873,requestid:5734f0bd-e4f6-4e0a-8fbc-622659b6e2e2,mobiledeviceid:863360024707550,userip:210.22.122.2"
#        print query_url
#        query_url = "http://192.168.5.149:4053/search/shop?query=geo%28poi,113.0231:28.19991,1000%29&sort=desc%28dpscore%29&fl=dist%28poi,113.0231:28.19991%29,shopid,shopname,shoppower,branchname,altname,power,shopgroupid,shoptype,cityid,defaultpic,avgprice,phone,address,crossroad,score1,score2,score2,dishtags,pictotal,hasbooksetting,dealgroupid,membercardid,membercardtitle,smspromoid,booktype,dealgrouptitle,dealgroupprice,contenttitle,hasticket,region1,category1,gpoi,isnewshop,shoptags,publictransit,businesshours,prepaidcards,hastakeaway,hasshortdeals,marketprice,poi,mopaystatus&limit=0,25&info=clientversion:6.5,app:PointShopSearch,platform:MAPI,referrequestid:013d92a7-a7eb-45b9-8534-5ccd0c176b1a,useragent:MApi+1.1+%28com.dianping.v1+6.5+om_sd_xiaomishichang+MI_3W;+Android+4.3%29,userlng:121.41542,queryid:f1efe724-9fb4-4e50-954a-e700f3c5e5a5,clientip:192.168.213.52,userlat:31.21746,sorttype:1,unrelatedguidefields:categoryids;regionids,geoFieldName:poi,mobileplatform:1,poi:113.0231:28.19991,wifi:,dpid:-7517157582792622873,requestid:5734f0bd-e4f6-4e0a-8fbc-622659b6e2e2,mobiledeviceid:863360024707550,userip:210.22.122.2"
        which_cmd = 'which wget'
        p = os.popen(which_cmd)
        abs_cmd = p.read().strip()
        mycmd = '%s -q "%s" -O %s' % (abs_cmd, query_url, tmpfile)
        os.system(mycmd)
        with open(tmpfile) as f:
            raw_data = json.loads(f.read())
            return raw_data['records']
    
    def parse_search_info(self, json_data=None, shopid=None):
        '''
        parse the search info (records) and do some calculation, then return a dict.
        '''
        
        res = {'shop_total_cnt' : len(json_data),
               'pos_index' : 0,
               'has_pic_cnt' : 0,
               'has_star_cnt' : 0,
               'has_review_cnt' : 0,
               'has_tg_cnt' : 0,
               'has_rs_cnt' : 0,
               'has_ta_cnt' : 0
                }
        for i, j in enumerate(json_data):
            if j['shopid'] == str(shopid):
                res['pos_index'] = i + 1
            if j['pictotal'] != "0":
                res['has_pic_cnt'] += 1
            if j['shoppower'] != "0":
                res['has_star_cnt'] += 1
            if j['votetotal'] != "0":
                res['has_review_cnt'] += 1
            if j['dealgroupid'] and j['dealgroupid'] != "0":
                res['has_tg_cnt'] += 1
            if j['hasbooksetting'] == "1":
                res['has_rs_cnt'] += 1
            if j['hastakeaway'] == "1":
                res['has_ta_cnt'] += 1
            
        return res
    
    def add_search_info_to_xml(self):
        '''
        add the search result to the POI xml file (currently I create a new XML file).
        '''
        
        poi_info_list = self.xml_to_poi_info_list()
        search_res_list = []
        for i in poi_info_list:
            search_info = self.get_search_info(i)
            search_res_list.append(self.parse_search_info(search_info, i[0]))
        xmldoc = minidom.parse(self.poi_xml)
        shops = xmldoc.getElementsByTagName('shop')
        for res, shop in zip(search_res_list, shops):
            search = xmldoc.createElement('search')
            for k in res:
                ele = xmldoc.createElement(k)
                ele_text = xmldoc.createTextNode(str(res[k]))
                ele.appendChild(ele_text)
                search.appendChild(ele)
            shop.appendChild(search)
        # if we don't use codecs.open(..'utf-8'), for e.g. open(), we'll meet a issue that 
        #      some Chinese characters can't be writed to the file (ascii format). 
        f = codecs.open(self.poi_with_search_xml, 'w', 'utf-8')  
        xmldoc.writexml(f, addindent='  ', newl='\n')  
        f.close()
            
                
if __name__ == '__main__':
#    poi = poi(searcher_host='10.1.1.158:4053')  # for production env
    poi = poi()
#    poi_info_list = poi.get_poi_info()
#    poi.poi_info_to_xml(poi_info_list)
    poi.add_search_info_to_xml()