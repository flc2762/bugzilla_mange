#/usr/bin/python
# -*- coding:utf-8 -*-
#from smb.SMBConnection import *
#from smb.base.ShareFile import *
#from smb.SMBProtocol import *

from smb.SMBConnection import SMBConnection

#SAMBA_USERNAME =  "apuser"
#SAMBA_PASSWORD = "123456"
#SAMBA_PORT = 139
#SAMBA_MYNAME = "apuser"
#SAMBA_REMOTEIP = "10.0.70.41"
#SAMBA_DOMAINNAME = "MYGROUPu"
#SAMBA_DOMAINNAME = ""
#SAMBA_DIR = 'bug_work'

SAMBA_USERNAME =  "lc.fan"
SAMBA_PASSWORD = "FLC@1712"
SAMBA_PORT = 445
SAMBA_MYNAME = "apuser"
SAMBA_REMOTEIP = "10.0.1.110"
SAMBA_DOMAINNAME = "MYGROUPu"
#SAMBA_DOMAINNAME = ""
SAMBA_DIR = 'hudson'

class ConnectSamba():

	def __init__(self,remoteip,sambadir,name,password):
		self.user_name = name
		self.pass_word = password
		self.my_name = SAMBA_MYNAME
		self.domain_name = SAMBA_DOMAINNAME
		self.remote_smb_IP = remoteip
		self.port = SAMBA_PORT
		self.dir = sambadir

	def downloadFile(self, sambafilepath, localfilepath,filename):
#        下载文件
#        :param filename: 保存到本地的文件名
#        :param download_filepath: 保存到本地文件的路径
#        :return:c
		try:
#			print "domain name %s" % self.domain_name
			conn = SMBConnection(self.user_name, self.pass_word, self.my_name, self.domain_name, use_ntlm_v2=True)
#			print 'connection %s ' % conn
			assert conn.connect(self.remote_smb_IP, self.port)
#			sharelist = conn.listPath('bug_work','')
#			print "dir %s " % sharelist
#			print "file name : %s " % filename
			file_obj = open(localfilepath + "/" + filename, 'wb')
			sambafilepath = sambafilepath + filename
			conn.retrieveFile(self.dir, sambafilepath, file_obj)
			file_obj.close()
			return True
		except :
			return False

	def uploadFile(self, filename, upload_path):
#        上传文件
#        :param filename: 上传文件的名称
#        :param upload_path: 上传文件的路径
#        :return:True or False
#	try:
		conn = SMBConnection(self.user_name, self.pass_word, self.my_name, self.domain_name, use_ntlm_v2=True)
		conn.connect(self.remote_smb_IP, self.port)
		file_obj = open(upload_path + filename, 'rb')
		conn.storeFile(self.dir, filename, file_obj)
		file_obj.close()
		return True
#	except:
#		return False

def samba_download_file(sambafilepath, localfilepath,filename):
	c = ConnectSamba()
	c.downloadFile(sambafilepath,localfilepath,filenam)

if __name__ == '__main__':
	samba_download_file('ShareData/CSDataRelease/Test_Products_Library/sprdroid7.0_trunk/MOCORDROID7.0_Trunk_K44_17C_ISharkL2/MOCORDROID7.0_Trunk_K44_17C_ISharkL2_W17.37.5/Images/sp9853i_1h10_v    mm_tos-userdebug-native/','./','symbols.vmlinux.sp9853i_1h10_vmm_tos_userdebug_native.tgz')
