#/usr/bin/python
# -*- coding:utf-8 -*-

import time
import os
from smb.SMBConnection import SMBConnection
import print_info

SAMBA_PORT = 445
SAMBA_MYNAME = "apuser"
SAMBA_DOMAINNAME = "MYGROUPu"

class download_samba():

    def __init__(self,remoteip,sambadir,user,password):
        self.user_name = user
        self.password = password
        self.my_name = SAMBA_MYNAME
        self.domain_name = SAMBA_DOMAINNAME
        self.remote_smb_ip = remoteip
        self.port = SAMBA_PORT
        self.dir = sambadir

    def download_samba_file(self, sambafilepath, localfilepath,filename):
        try:
            time_start = time.time()

            conn = SMBConnection(self.user_name, self.password, self.my_name, self.domain_name, use_ntlm_v2=True)
            print_string = 'samba connection %s' % conn
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
            assert conn.connect(self.remote_smb_ip, self.port)

            print_string = "local file path : %s" % (localfilepath + "/" + filename)
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
            file_fd = open(localfilepath + "/" + filename, 'wb')
            sambafilepath = sambafilepath + "/" + filename
            print_string = "samba file path : %s" % sambafilepath
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
            conn.retrieveFile(self.dir, sambafilepath, file_fd)

            time_use = time.time() - time_start
            file_size = os.path.getsize(localfilepath + r'/' + filename)
            samba_download_speed = (int)(file_size / time_use)

            file_fd.close()
            print_string = 'samba download file %s ok .\ndownload size %d use time is %0.2f s; speed is %d bit/s' % \
                           (filename, file_size, time_use, samba_download_speed)
            print_info.print_info(print_info.PRINT_INFO, print_string)
            return 1
        except Exception, e :
            print_string = "samba download file error %s" % e
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            return 0

    def upload_samba_file(self, filename, upload_path):
        try:
            conn = SMBConnection(self.user_name, self.password, self.my_name, self.domain_name, use_ntlm_v2=True)
            conn.connect(self.remote_smb_ip, self.port)
            file_fd = open(upload_path + filename, 'rb')
            conn.storeFile(self.dir, filename, file_fd)
            file_fd.close()
            print_info.print_info(print_info.PRINT_INFO, "samba upload file ok")
            return 1
        except Exception, e :
            print_string = "samba upload file error %s" % e
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            return 0


if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
    s= download_samba("10.0.1.110", 'hudson', "lc.fan", "FLC@1712")
    s.download_samba_file('ShareData/CSDataRelease/Test_Products_Library/sprdroid8.1_trunk/MOCORDROID8.1_Trunk_SHARKLE/MOCORDROID8.1_Trunk_SHARKLE_W17.48.5/Images/sp9832e_1h10_go_native-userdebug-native' ,
                    '/home/local/SPREADTRUM/lc.fan/flc/code/pybz',
                    'symbols.vendor.sp9832e_1h10_go_native_userdebug_native.tgz')