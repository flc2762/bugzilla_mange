import ConfigParser
import os

string_temp = ''
config = 0

class readconfig():
	def __init__(self):
		pass
	def read_item(self,item):
		string_temp = ''
		try :
			string_temp = config.get('info',item)
		except : 
#			print "get config item error"
			return (0,"get item error")
		else :
			if len(string_temp) :
				return (1,string_temp)
			else : 
#				print "get item is null"
				return (0,"get item is null")

	def read_config(self):
		global config
		global BUGZILLA_USERNAME
		global BUGZILLA_PASSWORD
		global KERNEL_MEMBERS
		global SEND_MAIL_ADDRESS
		global STATUS_FIELDS
		global PRODUCT_FIELDS
		global SAMBA_USERNAME
		global SAMBA_PASSWORD
		global SAMBA_REMOTEIP
		global TEST_BUGLIST
		get_item_ret = []
		config=ConfigParser.ConfigParser() 
		with open('./config','rw') as configfd: 
			config.readfp(configfd)

		get_item_ret = self.read_item('BUGZILLA_USERNAME')
		if get_item_ret[0] :
			BUGZILLA_USERNAME = get_item_ret[1]
			print 'BUGZILLA_USERNAME = %s ' % BUGZILLA_USERNAME
		
		get_item_ret = self.read_item('BUGZILLA_PASSWORD')
		if get_item_ret[0] :
			BUGZILLA_PASSWORD = get_item_ret[1]
			print 'BUGZILLA_PASSWORD = %s ' % BUGZILLA_PASSWORD

		get_item_ret = self.read_item('KERNEL_MEMBERS')
		if get_item_ret[0] :
			KERNEL_MEMBERS = get_item_ret[1].split(',')
			print 'KERNEL_MEMBERS = %s ' % KERNEL_MEMBERS

		get_item_ret = self.read_item('SEND_MAIL')
		if get_item_ret[0] :
			SEND_MAIL_ADDRESS = get_item_ret[1].split(',')
			print 'SEND_MAIL_ADDRESS =  %s ' % SEND_MAIL_ADDRESS

		get_item_ret = self.read_item('STATUS_FIELDS')
		if get_item_ret[0] :
			STATUS_FIELDS = get_item_ret[1].split(',')
			print 'STATUS_FIELDS =  %s ' % STATUS_FIELDS

		get_item_ret = self.read_item('PRODUCT_FIELDS')
		if get_item_ret[0] :
			PRODUCT_FIELDS = get_item_ret[1].split(',')
			print 'PRODUCT_FIELDS =  %s ' % PRODUCT_FIELDS

		get_item_ret = self.read_item('DEFAULT_FIELDS')
		if get_item_ret[0] :
			DEFAULT_FIELDS = get_item_ret[1].split(',')
			print 'DEFAULT_FIELDS =  %s ' % DEFAULT_FIELDS

		get_item_ret = self.read_item('SAMBA_USERNAME')
		if get_item_ret[0] :
			SAMBA_USERNAME = get_item_ret[1]
			print 'SAMBA_USERNAME = %s ' % SAMBA_USERNAME
		get_item_ret = self.read_item('SAMBA_PASSWORD')
		if get_item_ret[0] :
			SAMBA_PASSWORD = get_item_ret[1]
			print 'SAMBA_PASSWORD = %s ' % SAMBA_PASSWORD
		get_item_ret = self.read_item('SAMBA_REMOTEIP')
		if get_item_ret[0] :
			SAMBA_REMOTEIP = get_item_ret[1]
			print 'SAMBA_REMOTEIP = %s ' % SAMBA_REMOTEIP

		get_item_ret = self.read_item('TEST_BUGLIST')
		if get_item_ret[0] :
			TEST_BUGLIST = get_item_ret[1].split(',')
			print 'TEST_BUGLIST = %s ' % TEST_BUGLIST
		

if __name__ == '__main__':
	rdcgf = readconfig()
	rdcgf.read_config()
