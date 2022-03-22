# -*- coding: utf-8 -*-

'''
Created on Apr 21, 2014

'''

from StringIO import StringIO
import pycurl
import time
import os
from poi import poi


class app_poi(object):
    '''
    running DianPing App in an Andorid device or emulator.
        we assume DianPing App and my TestApp are already installed in the android system.
    '''

    upload_url = "http://qa-show-web02.nh/upload.php"
    adb = '/Users/jay/workspace/adt-bundle-mac-x86_64-20130917/sdk/platform-tools/adb'
    app_img_dir = '/mnt/sdcard/Robotium-Screenshots'

    def __init__(self):
        pass

    def clear_storage(self):
        '''
        clear the Robotium screen shot storage.
        '''

        clear_storage_cmd = '%s shell rm -f %s/*_*.jpg' % (self.adb, self.app_img_dir)
        os.system(clear_storage_cmd)

    def gen_img(self, poi_info=None, img_dir='img'):
        '''
        generate APP screen snapshot on different poi geo_location

        oi_info must be a list as [shopid, shopname, longitude, latitude, citiyid, cityname]
            e.g. [9125655, '龙马川菜馆', 119.940181, 31.969895, 93, '常州']
        '''

#        which_adb = 'which adb'
#        p = os.popen(which_adb)
#        adb = p.read().strip()
        cwd = os.getcwd()
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        cityid = poi_info[4]
        lng = poi_info[2]
        lat = poi_info[3]
        # image name is  $cityid_$shopid.jpg  '.jpg' will be automatically added in Robotium takecreenshot function.
        imgname = '%s_%s' % (cityid, poi_info[0])

        # currently, I assume there's only one android device/emulator running on the PC
        run_test_cmd = '%s shell am instrument -e lng %s -e lat %s -e cityid %s -e imgname %s ' % (self.adb, lng, lat, cityid, imgname)\
                + '-w com.dianping.v1.test/com.dianping.v1.test.MyTestRunner'
        os.system(run_test_cmd)
        time.sleep(20)
        os.chdir(img_dir)
        pull_img_cmd = '%s pull %s/%s.jpg %s.jpg' % (self.adb, self.app_img_dir, imgname, imgname)
        os.system(pull_img_cmd)
        time.sleep(2)
        os.chdir(cwd)  #need to change current dir to the previous dir.

        # return the absolute path of the image file
        return '%s/%s/%s.jpg' % (cwd, img_dir, imgname)

    def upload_img(self, mypic):
        '''
        upload the image to the remote server.
        '''

        storage = StringIO()
        c = pycurl.Curl()
        values = [
                  ("upload_file[]", (pycurl.FORM_FILE, str(mypic)))
                  ]
        c.setopt(c.URL, self.upload_url)
        c.setopt(c.WRITEFUNCTION, storage.write)
        c.setopt(c.HTTPPOST, values)
        c.perform()
        c.close()
        content = storage.getvalue()
        print content

if __name__ == '__main__':
    myapp = app_poi()
    myapp.clear_storage()
    poi = poi()
    poi_info_list = poi.xml_to_poi_info_list()
    for i in poi_info_list:
        mypic = myapp.gen_img(poi_info=i)
        myapp.upload_img(mypic)
#    myapp.upload_img('/Users/jay/workspace/aew_backend/qa-show/img/93_16887136.jpg')
