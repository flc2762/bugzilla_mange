import os
import requests   
#url = 'http://10.0.1.163:8080/jenkins/job/sprdroid8.0_trunk_sharkle/659/artifact/SYMBOLS/'
#url1 = 'http://10.29.1.51:8080/jenkins/job/sprdroid7.0_trunk_k44_isharkl2/752/artifact/Images/sp9853i_1h10_vmm_tos-userdebug-native/'
class MyHttp():
	def __init__(self):
		pass
#		print "downloading with urllib"
	def download_http(self, html_path, localfilepath, filename):
		urlrequest = 0
		fd = 0
#		print "downloading with requests"
		try :
			urlrequest = requests.get(html_path + filename,timeout = 10)
		except :
			return (0, 'time out')
		if int(urlrequest.status_code) > 400 :
			print 'get file error %d ' % int(urlrequest.status_code)
			return (0, 'get file error')
		print 'get file status %d ' % int(urlrequest.status_code)
		with open(localfilepath + r'/' + filename, "wb") as fd:
			fd.write(urlrequest.content)
		print 'get symbols end'
		if os.path.getsize(localfilepath + r'/' + filename) >= int(urlrequest.headers['content-length']) :
#			print 'local size %d  html size %d ' % (os.path.getsize(localfilepath + filename) ,int(urlrequest.headers['content-length']))
#			print 'get symbols ok'
			return (1,'get symbols ok')
		else :
#			print 'local size %d  html size %d ' % (os.path.getsize(localfilepath + filename) ,int(urlrequest.headers['content-length']))
			return (0,'get file size error')
#if __name__ == '__main__':
#	html = MyHttp()
#	html.download_http(url,'./','symbols.vmlinux.sp9832e_1h10_native_userdebug_native.tgz')
#	html.download_http(url1,'./','symbols.vmlinux.sp9853i_1h10_vmm_tos_userdebug_native.tgz')
