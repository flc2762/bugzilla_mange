#!/usr/bin/python

from rest import API 
import myftp
from mysamba import ConnectSamba
from myhttp import MyHttp
import socket_server
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time, os, sched,datetime
import smtplib
import os
import sys
import threading
import ConfigParser

CONFIG_VERSION = 0

#BUGINFO_SAVE = "/home/apuser/Downloads/bugs"
BUGINFO_SAVE = "."
main_save_path = "/home/apuser/bug_work/buglist"

#sysdump files download 
FTP_IP = "ftp.spreadtrum.com"
FTP_NAME = "spreadst"
FTP_PASSWORD = "spread$26?ST"

BUGZILLA_USERNAME = 'fanlc@spreadst.com'
BUGZILLA_PASSWORD = 'f1111111'

SAMBA_USERNAME = 'lc.fan'
SAMBA_PASSWORD = 'FLC@1712'
SAMBA_REMOTEIP = '10.0.1.110'
TEST_BUGLIST = ''

KERNEL_MEMBERS = ['zhaoxb@spreadst.com','wuls@spreadst.com','zhaoyd@spreadst.com','wangxz@spreadst.com','jianxing@spreadst.com','fanlc@spreadst.com','rangsn@spreadst.com','Hao_hao.Wang@spreadtrum.com','jia.hou@spreadtrum.com','changjr@spreadst.com']
SEND_MAIL_ADDRESS = ['zhaoxb@spreadst.com','wuls@spreadst.com','zhaoyd@spreadst.com','jianxing@spreadst.com','fanlc@spreadst.com','rangsn@spreadst.com','changjr@spreadst.com']
#SEND_MAIL_ADDRESS = ['fanlc@spreadst.com']
STATUS_FIELDS = ["NEW","Assigned"]
PRODUCT_FIELDS = ["Sprdroid_7.0_iWhale2","Sprdroid_7.0_iSharkL2","Sprdroid8.0_SharkLE"]

DEFAULT_FIELDS = ["id", "status", "product","assigned_to","summary", "whiteboard","cf_base_on_ver"]


SETTABLE_FIELDS = ["alias", "assigned_to", "blocks", "depends_on", "cc",
    "comment", "component",   "deadline", "dupe_of", "estimated_time",
    "groups", "keywords", "op_sys","platform", "priority", "product",
    "qa_contact", "reset_assigned_to", "reset_qa_contact", "resolution",
    "see_also", "status", "summary", "target_milestone", "url",
    "version", "whiteboard"]

CREATING_FIELDS = ["product", "component", "summary", "version",
    "description", "op_sys", "platform", "priority", "severity",
    "alias", "assigned_to", "cc", "groups", "qa_contact", "status",
    "resolution", "target_milestone"]

GETTING_FIELDS = ["alias", "assigned_to", "blocks", "cc",
    "classification", "component", "creation_time", "creator",
    "deadline", "depends_on", "dupe_of", "estimated_time", "groups",
    "id", "is_confirmed", "is_open", "keywords", "last_change_time",
    "op_sys", "platform", "priority", "product", "qa_contact",
    "remaining_time", "resolution", "see_also", "severity", "status",
    "summary", "target_milestone", "url", "version", "whiteboard"]

default_params = {'product': 'Sprdroid_7.0_iWhale2','status': 'Duplicate', 'assigned_to': 'wangxz@spreadst.com'}

schedule = sched.scheduler(time.time, time.sleep)
time_num = 0

ftp_password_flag = 0
socket = 0
dispense_flags = 1
current_bug_all = {}
kernel_group_buglist_now = []
kernel_group_buglist_old = []
kernel_group_buglist_new = []
download_timeout_buglist = []
no_file_buglist = []
no_file_bug_num = []
download_bug_list_temp = []
download_bug_list_dispense = []
download_temp_bugid = 0
download_temp_bug_path = []

def send_email(mymsg,you):
	#me = "xz.wang@spreadtrum.com"
	#my_password = r"1qaz_2wsx"
	#me = "wxz007886@163.com"
	me = "fanlc@spreadst.com"
	#my_password = r"zhenaixueni1234"
	my_password = r"fanlc123456789"
	#you = "wangxianzhen@aliyun.com"
	msg = MIMEMultipart('alternative')
	#msg['Subject'] = "Alert"
	time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	msg['Subject'] = "Kernel group bugs Statistics ---- %s " % time_now
	msg['From'] = me
	msg['To'] = you 
	msg["Accept-Language"]="zh-CN"
	msg["Accept-Charset"]="ISO-8859-1,utf-8"
	#html = '<html><body><p>Hi, I have the following alerts for you!</p></body></html>'
	html = '<html><body><p>%s</p></body></html>' % mymsg
	part2 = MIMEText(html, 'html',sys.getfilesystemencoding())

	msg.attach(part2)

	s = smtplib.SMTP_SSL('mail.spreadst.com')
	s.login(me, my_password)

	s.sendmail(me, you, msg.as_string())
	s.quit()

def print_bug(b, output_fields):                                                                                                                                                                
	fields = []
	fields_contents = {}
	index = 0 
	for f in output_fields:
		if f in b:
			fields.append(str(b[f]))
			fields_contents[f] = str(b[f])
	print fields_contents
	#return "    ".join(fields) + '\n'
	return fields_contents

def add_bugid(theIndex,word,bugid ):
	theIndex.setdefault(word, [ ]).append(bugid)

def list_bug_summary(api,bugid):
	params = {}
	add_bugid(params,'id',bugid)	
	for b in api.bug_get(params):
		print_bug (b, DEFAULT_FIELDS)
	
def list_members_bugs_single(api, product, member, status):
	s = ''
	bug_info_list = []
	fields = []
	if not member :
		print "use default params :" 
		print  default_params
		for b in api.bug_get(default_params):
			s += print_bug (b, DEFAULT_FIELDS)
	else :
		params = default_params
		params.update({"status":status}) 
		params.update({"assigned_to":member}) 
		params.update({"product":product}) 
		for b in api.bug_get(params):
			bug_info = {}
			for f in DEFAULT_FIELDS:
				if f in b :
					bug_info[f] = str(b[f])
			bug_info_list.append(bug_info) 
	return bug_info_list 
		
def mytest(api,bugid):
	params = {}
	add_bugid(params,'id',bugid)	
	for b in api.bug_get(params):
	        output_fields = ['id']
	        fields = []
	        for f in output_fields:
        	    if f in b:
                	fields.append(str(b[f]))
        	print " ".join(fields)

def bug_info_save_write(path,log_name,contents):
	save_file = path + '/' + log_name
	f = open(save_file,'w+')
	f.write(contents)
	f.close()
def bug_info_read_data(path,log_name):
	read_file = path + '/' + log_name
	f = open(read_file,'r')
	data = f.read()
	f.close()
	return data

def bug_info_save_append(path,log_name,contents):
	save_file = path + '/' + log_name
	f = open(save_file,'ab')
	f.write(contents)
	f.close()

def bug_info_read_line(path,log_name):
	read_file = path + '/' + log_name
	f = open(read_file,'r')
	lines = f.readlines()
	f.close()
	return lines

def get_sysdump(bugid,logpath):
	download_log_status = []
	global download_timeout_buglist
	global no_file_buglist
	global no_file_bug_num
	global download_bug_list_temp
	global dispense_flags
	global ftp_password_flag
	global download_bug_list_dispense
	global main_save_path

        print "get sysdump files ,path is :\n%s" % logpath
	bug_info_save_append(main_save_path,'.kernel_python_log' + datetime.datetime.now().strftime('%Y-%m-%d'),"get sysdump files path is " + logpath + '\n')

        des_str_len = len(FTP_IP)
        des_str_start = logpath.find(FTP_IP)
        str_len_sum = len(logpath)
        ftp_filepath = logpath[(des_str_start + des_str_len ):str_len_sum]
        path_split = os.path.split(ftp_filepath)
#        print 'gen log name %s' % path_split[1]
	if len(kernel_group_buglist_new) > 0 : 
		bug_info_save_append(main_save_path,'bug_id_statistics','download bug id log ' + str(bugid) + ' start\n')
        ftp = myftp.MyFTP(dispense_flags,main_save_path)
	if 0 == ftp_password_flag :
        	download_log_status = ftp.download(FTP_IP,21, FTP_NAME,FTP_PASSWORD,ftp_filepath,bugid)
	else :
		download_log_status = ftp.download(FTP_IP,21, 'StabTest', '2lKs68kg',ftp_filepath,bugid)
 		
	if download_log_status[0] :
		if myftp.socket_link_num == 0:
			bug_info_save_append(main_save_path,'bug_id_statistics','download bug id log ' + str(bugid) + ' end\n')
			socket_server.download_ok_list.append(bugid)
#			if bugid in download_bug_list_dispense :
#				download_bug_list_dispense.pop(download_bug_list_dispense.index(bugid))
		else : 
			if bugid not in download_bug_list_dispense:
				download_bug_list_dispense.append(bugid)
#		if bugid in download_bug_list_dispense :
#			download_timeout_buglist.pop(download_bug_list_dispense.index(bugid))
		if bugid in download_timeout_buglist :
			download_timeout_buglist.pop(download_timeout_buglist.index(bugid))
		if bugid in no_file_buglist :
			no_file_bug_num.pop(no_file_buglist.index(bugid))
			no_file_buglist.pop(no_file_buglist.index(bugid))
	else :
		print "\nerror : download %s error : %s" % (str(bugid), download_log_status[1])
		if bugid in download_bug_list_dispense :
			download_timeout_buglist.pop(download_bug_list_dispense.index(bugid))
		if 'time out' in download_log_status[1] :
			if bugid not in download_timeout_buglist :
				download_timeout_buglist.append(bugid) 
				if bugid in no_file_buglist :
					no_file_bug_num.pop(no_file_buglist.index(bugid))
					no_file_buglist.pop(no_file_buglist.index(bugid))
		elif 'not find file' in download_log_status[1] :
			if bugid not in no_file_buglist :
				no_file_buglist.append(bugid)
				no_file_bug_num.append(0)
				if bugid in download_timeout_buglist : 
					download_timeout_buglist.pop(download_timeout_buglist.index(bugid))
			elif no_file_bug_num[no_file_buglist.index(bugid)] > 5:
				no_file_bug_num.pop(no_file_buglist.index(bugid))
				no_file_buglist.pop(no_file_buglist.index(bugid))
				bug_info_save_append(main_save_path,'bug_id_statistics','download bug id log ' + str(bugid) + ' error\n')
			else :
				no_file_bug_num[no_file_buglist.index(bugid)] += 1
		elif "login failed" in download_log_status[1] :
			if bugid not in download_timeout_buglist and bugid not in no_file_buglist :
				download_timeout_buglist.append(bugid) 
		else :
			bug_info_save_append(main_save_path,'bug_id_statistics','download bug id log ' + str(bugid) + ' error\n')
	if bugid not in download_bug_list_temp :
		download_bug_list_temp.append(bugid)
	return download_log_status

def get_symbols(sambadir, sambafilepath, localfilepath, filename):
	print "get symbols files,path is : \n%s " % sambafilepath
#	print "get symbols file name : %s " % filename
	downloadsymbols = 0
	readdownloadstatus = ''
	localfilepathname = ''
	#exist symbols file 
	if os.path.exists(localfilepath + '/.symbols_status') :
		readdownloadstatus = bug_info_read_line(localfilepath,'.symbols_status')
#	print readdownloadstatus
	for x in readdownloadstatus:
		if '3' in x :
			downloadsymbols = 3
#			print 'downloadsymbols : %d' % downloadsymbols
	
	if downloadsymbols != 3 :
		#download symbols file
		print 'download %s ...' % filename
		bug_info_save_write(localfilepath,'.symbols_status',"symbols:4:1")
		smb = ConnectSamba(SAMBA_REMOTEIP,sambadir,SAMBA_USERNAME,SAMBA_PASSWORD)
		downloadsymbols = smb.downloadFile(sambafilepath,localfilepath,filename)
	
		#save download symbols file status
		if downloadsymbols :
			bug_info_save_write(localfilepath,'.symbols_status',"symbols:3:1")
			print "get symbols %s end" % filename
		else :
			#download error remove file
			localfilepathname = localfilepath + '/' + filename
			if os.path.exists(localfilepathname):
				os.remove(localfilepathname)
			bug_info_save_write(localfilepath,'.symbols_status',"symbols:0:1")
			print "error : get symbols %s error" % filename

def get_symbols_form_http(httpdir, httpfilepath, localfilepath, filename) :
#	print "get symbols files form http ,path is : \n%s " % httpfilepath
#	print "get symbols file name : %s " % filename
	httpdownloadsymbols = 0
	readdownloadstatus = ''
	localfilepathname = ''
	httppath = httpfilepath + 'artifact/SYMBOLS/'
	ret = []
	#exist symbols file 
	if os.path.exists(localfilepath + '/.symbols_status') :
		readdownloadstatus = bug_info_read_line(localfilepath,'.symbols_status')
#	print readdownloadstatus
	for x in readdownloadstatus:
		if '3' in x :
			httpdownloadsymbols = 3
#			print 'downloadsymbols : %d' % downloadsymbols
	
	if httpdownloadsymbols != 3 :
		#download symbols file
		print 'download %s form http...' % filename
		print 'download symbols path : %s from http' %  httppath
		bug_info_save_write(localfilepath,'.symbols_status',"symbols:4:2")
		http = MyHttp()
		ret = http.download_http(httppath,localfilepath,filename)
	
		#save download symbols file status
		if ret[0] :
			bug_info_save_write(localfilepath,'.symbols_status',"symbols:3:2")
			print "get symbols %s form http end" % filename
		elif 'get file error' in ret[1] :
			httppath = httpfilepath + 'artifact/Images/' + httpdir + '/'
			ret = http.download_http(httppath,localfilepath,filename)
			if ret[0] :
				bug_info_save_write(localfilepath,'.symbols_status',"symbols:3:2")
				print "get symbols %s form http end" % filename
			else :
				#download error remove file
				localfilepathname = localfilepath + '/' + filename
				if os.path.exists(localfilepathname):
					os.remove(localfilepathname)
				bug_info_save_write(localfilepath,'.symbols_status',"symbols:0:2")
				print "error : get symbols %s from http error" % filename

def get_kernel_bug_all(api):
	bugs_info_all = []
	for p in  PRODUCT_FIELDS :
		print "get %s bug..." % p
		for m in  KERNEL_MEMBERS :
			for s in STATUS_FIELDS :
				list_a_bug = list_members_bugs_single(api,p,m,s)
				if  len(list_a_bug):
					for x in list_a_bug:
						bugs_info_all.append(x)
	return bugs_info_all
	
def get_bug_id_info(api,bugid):
	params = {'id': bugid}
        bug_data = api.bug_get_id_all_info(params)
	print bug_data
	return bug_data

def get_bug_files(api,bugid):
	logpath = ''
	logfilename = ''
	logftpserver = ''
	symbolsname = ''
	symbolsdir = ''
	symbolscut = []
	symbolsnamehttp = ''
	symbolsdirhttp = ''
	symbolscuthttp = []
	version_path_samba = ''
	version_path_samba_dir = ''
	version_path_samba_cut = []
	version_path_jenkins = ''
	version_path_jenkins_pac = ''
	global ftp_password_flag
	global download_bug_list_temp
	global main_save_path
	downloadsymbolsthread = 0
	downloadsymbolsthreadhttp = 0
	ret = []
	#print "Show bug: %s files info ." % bugid
	params = {'id': bugid}
        bug_data = api.bug_get_all_info(params)
#	print "################all comment###########################\n"
#	print bug_data
        first_comment =  bug_data['bugs'][str(bugid)][bug_data.keys()[1]][0]
#	print "################comment 0##################################\n"
#	print first_comment
	first_comment_text = first_comment[first_comment.keys()[3]].split('\n')
#	print "##############first_comment_text############################\n"
#	print first_comment.keys()
#	print first_comment_text
	if len(first_comment_text) > 0:	
	        for x in first_comment_text:
#			print x
			#L(l)oglujing + bugID.rar -----727619 738276 738941 741537
#			if u'Log\u8def\u5f84' in x or u'log\u8def\u5f84\uff1a' in x :
				#delete u'log\u8def\u5f84\uff1a' ------738941
			if r'\TestLogs' in x :
				if not len(logpath) :
					logpath = x[x.index(r'\TestLogs'):]
#					print "log TestLogs path : %s" % logpath
					continue
			if r'\Testlogs' in x : 
				if not len(logpath) :
					logpath = x[x.index(r'\Testlogs'):]
#					print "log Testlogs path : %s" % logpath
					continue
#				if ':' in x:
#					logpath = x.split(':')[1]
#				print "log : path : %s" % logpath 
#				continue 
			#waiwang \\shnas02 + Logfile----------737797 741351
#			if len(logpath) == 0 :
				#waiwang
#				if u'\u5916\u7f51' in x:
#				if r'\TestLogs' in x:
#					logpath = x[x.index(r'\TestLogs'):]
#				continue
			#get logfilename--------736380
			if '.rar' in x :
				if 'bug' in x :
					logpath = logpath
				else :
					logfilename = x
#					print 'log file name : %s' % logfilename
				continue
			#get ftpserver
	                if 'ftp.spreadtrum.com' in x:
				if not len(logftpserver) :
	                	       	logftpserver = x
#					print "log ftp server : %s" % logftpserver
			if 'Project' in x :
				if not len(symbolsname) :
					if 'sp' in x :
						symbolsname = x[x.index('sp'):]
						symbolscut = symbolsname.split('_')
						#get symbols file name and symbols dir 
						for y  in symbolscut :
							if '-' in y :
								symbolsname = symbolsdir
								symbolsdir = symbolsdir + y
								symbolsname = 'symbols.vmlinux.' + symbolsname + y.replace('-','_') + '.tgz'
#								print 'symbolsname %s' % symbolsname
#								print 'symbolsdir %s' % symbolsdir
								break;
							symbolsdir = symbolsdir + y + '_'
			#get vmlinuxserver
	                if '10.0.1.110' in x:
				if ':' in x :
	                        	version_path_samba = x.split(':')[1]
				else :
					version_path_samba = x
			#get vmlinux jenkins server
	                if 'jenkins' in x:
				if 'http' in x :
	                        	version_path_jenkins = x[x.index('http'):]
			if 'Pac:' in x:
				if not len(symbolsnamehttp) :
					if 'sp' in x:
						symbolsnamehttp = x[x.index('sp'):]

        #get log path and download it
	if r'(' in logpath :
		# delete bug 740894 zhongwenzifu 741537
		logpath = logpath[:logpath.index(r'(')]
	if u'\uff08' in logpath :
		# delete bug 741537 zhongwenzifu
		logpath = logpath[:logpath.index(u'\uff08')]                                         
	if len(logpath) >0 :
		#join log path,replace '\\' and 'bugID',delete spaces--------------727619 738276
		if 'bugID' in logpath :   
			logpath = logpath.replace('bugID',str(bugid)).replace('\\','/').strip()
		elif 'BugID' in logpath :   
			logpath = logpath.replace('BugID',str(bugid)).replace('\\','/').strip()
		elif 'bugid' in logpath :   
			logpath = logpath.replace('bugid',str(bugid)).replace('\\','/').strip()
		#jion log path,replace '\\' ,delete spaces,delete '\\shnas02\TestData' in logpath------------------736380
		elif len(logfilename) > 0 :
			logpath = logpath +'/'+ logfilename
			logpath = logpath[logpath.index(r'\TestLogs'):].replace('\\','/').strip()
		#jion log path ,replace '\\', add logfilename (str(bugid)+'.rar')-------------------737797 738941
		elif r'\TestLogs' in logpath or r'\Testlogs' in logpath :
			#log filename in log path--------------------740436 739513
			logfilename = logpath[logpath.rfind('\\')+1:]
#			print "find log file name % s" % logfilename	
			if r'.rar' in logfilename or r'.zip' in logfilename or r'.7z' in logfilename : 
				logpath = logpath.replace('\\','/')
			elif not len(logfilename) :
				logpath = logpath.replace('\\','/') + str(bugid) +'.rar'
			else :
				logpath = logpath.replace('\\','/') + '/' + str(bugid) +'.rar'
		#jion log path --------------------------------------737832
		else :
			logpath = '/' + logpath.replace('\\','/') + '/' + str(bugid) +'.rar'
#		print "Log : %s " % logpath
		#jion ftpserver and logpath
		if len(logftpserver) > 0:
			logftpserver = r'ftp://ftp.spreadtrum.com'	
#			print "ftp server : %s" % logftpserver
			logpath = logftpserver + logpath
#			print "all path : %s" % logpath
		ftp_password_flag = 0
	# logpath is null,logpath in logftpserver -----------738373
	else :
		if 'BugID' in logftpserver :
			logpath = logftpserver.replace('BugID',str(bugid)) + '.rar'
			#sharklE
			if r'/sharkle/' in logpath:
				logpath = logpath.replace(r'/sharkle/',r'/sharklE/')
			ftp_password_flag = 1
		if '.gz' in logftpserver :
			logpath = logftpserver
			ftp_password_flag = 0
#		print "BJ all path : %s" % logpath

	#mkdir path bugid
	localfilepath = main_save_path + r'/' + str(bugid)
	if not  os.path.exists(localfilepath) :
		os.mkdir(localfilepath)
	
	if len(current_bug_all) :
		for bugid_info in current_bug_all :
			if bugid == bugid_info['id']:
				print 'bug product %s' % (bugid_info['product'])
				if not  os.path.exists(localfilepath+'/'+'.bugid_info') :
					bug_info_save_write(localfilepath,'.bugid_info',(bugid_info['product']))
	

	#test get vmlinux
	if len(version_path_samba) > 0:
#		print 'samba path : %s' % version_path_samba
		#get samba path
		if '10.0.1.110\\' in version_path_samba :
			version_path_samba = version_path_samba[version_path_samba.index('10.0.1.110\\') + 11:].strip()
#			print 'delete 110 : %s' % version_path_samba
			version_path_samba_cut = version_path_samba.split('\\')
#			print 'path cut %s ' % version_path_samba_cut
			version_path_samba_dir = version_path_samba_cut[0]
#			print 'samba dir %s '%  version_path_samba_dir
			version_path_samba = version_path_samba[version_path_samba.index(version_path_samba_cut[1]):]
#			print 'samba path %s ' % version_path_samba
#		if 'ShareData\\' in version_path_samba :
#			version_path_samba = version_path_samba[version_path_samba.index('ShareData\\'):]
#			print "cut ShareData %s " % version_path_samba
		# add \Images
		if '\Images' not in version_path_samba :
			version_path_samba = version_path_samba + '\Images'
		else : 
			version_path_samba = version_path_samba[:version_path_samba.index('\Images')+7]
		#join samba path add symbols dir
		version_path_samba = version_path_samba.replace('\\','/') + '/' + symbolsdir + '/'
#		print "samba Version : %s " % version_path_samba
		# create thread download symbols
		if len(symbolsname) > 0 :
			downloadsymbolsthread = threading.Thread(target=get_symbols,args=(version_path_samba_dir,version_path_samba,localfilepath,symbolsname),name='downloadsymbols') 
			downloadsymbolsthread.setDaemon(True)
			downloadsymbolsthread.start()
#			print 'live : %s' % int(downloadsymbolsthread.is_alive())
	
	if len (version_path_jenkins) > 0 :
		print "jenkins : %s " % version_path_jenkins
		if not len(symbolsnamehttp) :
			if len(current_bug_all) :
				for bugid_info in current_bug_all :
					if bugid == bugid_info['id']:
						print 'Base_On_Version %s' % (bugid_info['cf_base_on_ver'])
						symbolsnamehttp = bugid_info['cf_base_on_ver']
		symbolscuthttp = symbolsnamehttp.split('_')
		#get symbols file name and symbols dir for http 
		for y in symbolscuthttp :
			if '-' in y :
				symbolsnamehttp = symbolsdirhttp
				symbolsdirhttp = symbolsdirhttp + y
				symbolsnamehttp = 'symbols.vmlinux.' + symbolsnamehttp + y.replace('-','_') + '.tgz'
				print 'symbolsnamehttp %s' % symbolsnamehttp
				print 'symbolsdirhttp %s' % symbolsdirhttp
				break;
			symbolsdirhttp = symbolsdirhttp + y + '_'
		downloadsymbolsthreadhttp = threading.Thread(target=get_symbols_form_http,args=(symbolsdirhttp, version_path_jenkins, localfilepath, symbolsnamehttp),name='downloadsymbolshttp')
		downloadsymbolsthreadhttp.setDaemon(True)
		downloadsymbolsthreadhttp.start()

#	get logpath size 
	if len(logpath) > 3 : 
		ret =  get_sysdump(bugid,logpath)
		for x in range(10) :
			if 'time out' in ret[1]:
				ret =  get_sysdump(bugid,logpath)
				print "get sysdump timeout try again %d " %  x
			else : 
				break
	else : 
		if bugid not in download_bug_list_temp :
			download_bug_list_temp.append(bugid)

def downloadlog(api,loglist) :
	global download_bug_list_temp
	download_bug_list_temp = []
	for x in loglist :
		print 'download id %s log...' % x
		bug_info_save_append(main_save_path,'.kernel_python_log' + datetime.datetime.now().strftime('%Y-%m-%d'),"download id  " + x + 'log ...' + '\n')
		get_bug_files(api,x)
#	loglist = []
				
##############################		config file ######################################
config_list = ['KERNEL_MEMBERS', 'API_PARAMETERS', 'PRODUCT_FIELDS', 'SRC_EMAIL_PADDWORD', 'BUGZILLA_COUNT', 'FTP_PASSWORD', 'DE_EMAIL_NAME', 'FTP_NAME', 'SRC_EMAIL_NAME', 'FTP_HOST']

def get_api_params_tuple(config):
        for x in config.keys():
                if x == 'API_PARAMETERS':
                        api_params = config[x].split(',')
                        list_index = 0
                        for x in api_params:
                                api_params[list_index ] =  x.replace('\n','')
                                list_index += 1
        return tuple(api_params)

def get_bugzilla_count_tuple(config):
        for x in config.keys():
                if x == 'BUGZILLA_COUNT':
                        bugzilla_count = config[x].split(',')
                        list_index = 0
                        for x in bugzilla_count:
                                bugzilla_count[list_index ] =  x.replace('\n','')
                                list_index += 1
        return tuple(bugzilla_count)


#####################		time sch part		####################################

def do_task(cmd):
	# we only do this work time range 8~21, exculde saturday and sunday
	global time_num
	try :
		now =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		now = int(now.split(' ')[1].split(':')[0])
		day_of_week = datetime.datetime.now().weekday()
		if time_num > 12 :
			bug_info_save_append(main_save_path,'.kernel_python_log' + datetime.datetime.now().strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '----------\n')
		if day_of_week < 5 :
			if (now > 7) & (now < 22):
				snapshot()
			else:
				if time_num > 12:
					time_num = 0
					snapshot()
				else : 
					time_num = time_num + 1
#			print 'Do not send email .day_of_week is :%s	now is: %s' % (day_of_week,now)
		else:
			if time_num > 12:
				time_num = 0
				snapshot()
			else : 
				time_num = time_num + 1
#			print 'Not on duty .Do not send email .day_of_week is :%s	now is: %s' % (day_of_week,now)
	except Exception, e:
		print 'error : run error : %s' % e
		#save except log to .kernel_python_log
		bug_info_save_append(main_save_path,'.kernel_python_log' + datetime.datetime.now().strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n' + str(e) + '\n')

def perform_command(cmd,inc):
        do_task(cmd)
        schedule.enter(inc, 0, perform_command, (cmd,inc))

def timming_exe(inc ):
        cmd = ''
	perform_command(cmd,inc)
#        schedule.enter(inc, 0, perform_command, (cmd,inc))
        schedule.run()


def bug_id_list_read(path,log_name):
	id_list = ''
	file_lines = bug_info_read_line(path,log_name)
	for line in file_lines :
		if r'bugid :' in line :
			#delete  'bugid : ', 8byte
			id_list = line[8:]
	return id_list

bugs_table_title = {'Kernel_bugs':PRODUCT_FIELDS}

def get_bug_id_list(*current_bug_all):
	bugs_id_list = []
	bugs_all = current_bug_all[0]
	for bug_dict in bugs_all:
		for key in bug_dict.keys():
			if key == 'id':
				bugs_id_list.append(bug_dict[key])
	return bugs_id_list			




def get_bugs_info_str(*current_bug_all):
	bugs_all = current_bug_all[0]
	bugs_info_str = []
	bugs_info_str.append('    ')
	s = ''
	for bug_dict in bugs_all:
		for f in DEFAULT_FIELDS:
			if f in bug_dict.keys():
				bugs_info_str.append(str(bug_dict[f]))
		bugs_info_str.append('\n')
	
	s = "    ".join(bugs_info_str)
	return s



def make_bugs_table_contents(*current_bug_all):
	bugs_table_contents = {'Total':[0,0,0]}
	bugs_sum_table = []
	bugs_all = current_bug_all[0]
	for x in KERNEL_MEMBERS:
		bugs_table_contents[x] = [0,0,0]
	for bug_dict in bugs_all:
		for key in bug_dict.keys():
			if key == 'product':
				if bug_dict[key] == 'Sprdroid_7.0_iWhale2':
					index = 0
				if bug_dict[key] == 'Sprdroid_7.0_iSharkL2':
					index = 1
				if bug_dict[key] == 'Sprdroid8.0_SharkLE':
                                        index = 2

			if key == 'assigned_to':
				if bug_dict[key] in KERNEL_MEMBERS:
					bugs_table_contents[bug_dict[key]][index] += 1
					bugs_table_contents['Total'][index] += 1
	bugs_sum_table.append(bugs_table_contents)
	return bugs_sum_table



def show_bugs_table(*bugs_table):
	bugs_table_contents = bugs_table[0][0]
	for key,value in bugs_table_title.items():
		print '|'+'%40s' % key + '|' + '%40s' % value[0] + '|'  + '%40s' % value[1] + '|'
	for key,value in bugs_table_contents.items():
		print '|'+'%40s' % key + '|' + '%40s' % value[0] + '|'  + '%40s' % value[1] + '|'
def save_bugs_table(*bugs_table):

	bugs_table_contents = bugs_table[0][0]
	file_contents = ''

	for key,value in bugs_table_title.items():
		file_contents = file_contents + '|'+'%40s' % key + '|' + '%40s' % value[0] + '|'  + '%40s' % value[1] + '|' + '%40s' % value[2] + '|' +  '\n'
	for key,value in bugs_table_contents.items():
		if key != 'Total' :
			file_contents = file_contents + '|'+'%40s' % key + '|' + '%40s' % value[0] + '|'  + '%40s' % value[1] + '|' + '%40s' % value[2] + '|' + '\n'
	#add Total to file_contents end
	file_contents = file_contents + '|'+'%40s' % 'Total' + '|' + '%40s' % bugs_table_contents['Total'][0] + '|'  + '%40s' % bugs_table_contents['Total'][1] + '|' + '%40s' % bugs_table_contents['Total'][2] + '|' + '\n'
	
	return file_contents

def make_html_table(name,score):
	if score < 60:  
		return '<tr><td>%s</td><td style="color:red">%s</td></tr>'% (name,score)
	else:
		return '<tr><td>%s</td><td>%s</td></tr>' %  (name,score)
def email_html_table(*bugs_table):

	file_contents = ''
	bugs_table_contents = bugs_table[0][0]
	table_tile = '<font color="#FF0000"> Kernel Group bugs statistics:</font> \n' 
	tds = []
	#tds = [make_html_table(name,score) for name, score in d.iteritems()]
	for name,score in bugs_table_contents.items():
		if name != 'Total' :
			tds.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %  (name,score[0],score[1],score[2],score[0] + score[1] + score[2]))
	tds.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %  ('Total',bugs_table_contents['Total'][0],bugs_table_contents['Total'][1],bugs_table_contents['Total'][2],bugs_table_contents['Total'][0] + bugs_table_contents['Total'][1] + bugs_table_contents['Total'][2]))
	file_contents = file_contents + '<table border="1">'
	file_contents = file_contents + '<caption>'
	file_contents = file_contents + u'%s' % table_tile.replace('\n','<br>')
	file_contents = file_contents + '</caption>'
	file_contents = file_contents + '<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>Total</th><tr>' % (bugs_table_title.keys()[0], bugs_table_title.values()[0][0], bugs_table_title.values()[0][1], bugs_table_title.values()[0][2])
	file_contents = file_contents + '\n'.join(tds)
	file_contents = file_contents + '</table>'
	return file_contents
	
def email_html_table_bug_detail(*bug_detail_list):
	table_tile = '<font color="#FF0000"> Kernel Group bugs Detail: </font> \n' 
	file_contents = ''
	tds = []
	font_color_flag = 0
	bug_info_dict_list = bug_detail_list[0]

	for bug_dict in bug_info_dict_list: 
		tds.append('<tr>')
                for f in DEFAULT_FIELDS:
                        if f in bug_dict.keys(): 
				for x in kernel_group_buglist_new :
					if x == bug_dict['id'] :
						font_color_flag = 1
				if font_color_flag :
					font_color_flag = 0
					tds.append('<td><font color="#FF0000">%s</font></td>' % bug_dict[f])
				else:
					tds.append('<td>%s</td>' % bug_dict[f])
		tds.append('<tr>')

	file_contents = file_contents + '<table border="1">'
	file_contents = file_contents + '<caption>'
	file_contents = file_contents + u'%s' % table_tile.replace('\n','<br>')
	file_contents = file_contents + '</caption>'
	file_contents = file_contents + '<tr>'
	for x in DEFAULT_FIELDS:
		file_contents = file_contents + '<th>%s</th>' % x
	file_contents = file_contents + '<tr>'
	file_contents = file_contents + '\n'.join(tds)
	file_contents = file_contents + '</table>'
	
	return file_contents	
def email_html_table_download_ok_bug(*bug_detail_list):
	file_contents = ''
	tds = []
	font_color_flag = 0
	bug_info_dict_list = bug_detail_list[0]

	file_contents += "\ndownload bug log ok: \n" + str(socket_server.download_ok_list) +'\n\n'
	file_contents +="get bug log from:'apuser@10.0.70.41:/home/apuser/bug_work/buglist/bugid' password:123456\nor\nget bug log from:'smb://10.0.70.41/bug_work' login:apuser passwor:123456"
	file_contents = file_contents.replace('\n','<br>')
	socket_server.download_ok_list = []

#	table_tile = '<font color="#FF0000"> download bug log ok : </font> \n'
#	for bug_dict in bug_info_dict_list: 
#		tds.append('<tr>')
#		for x in kernel_group_buglist_new :
#			if x == bug_dict['id'] :
#				for f in DEFAULT_FIELDS:
#					if f in bug_dict.keys(): 
#						tds.append('<td>%s</td>' % bug_dict[f])
#		tds.append('<tr>')
#
#	file_contents = file_contents + '<table border="1">'
#	file_contents = file_contents + '<caption>'
#	file_contents = file_contents + u'%s' % table_tile.replace('\n','<br>')
#	file_contents = file_contents + '</caption>'
#	file_contents += "\ndownload bug log ok: \n" + str(download_ok_list) +'\n\n'
#	file_contents += "get bug log from: 'apuser@10.0.70.41:/home/apuser/bug_work/buglist/bugid' <password:123456>\nor\nget bug log from: 'smb://10.0.70.41/bug_work' <login:apuser passwor:123456>"
#	file_contents = file_contents.replace('\n','<br>')
#	file_contents = file_contents + '<tr>'	
#	for x in DEFAULT_FIELDS:
#		file_contents = file_contents + '<th>%s</th>' % x
#	file_contents = file_contents + '<tr>'
#	file_contents = file_contents + '\n'.join(tds)
#	file_contents = file_contents + '</table>'

	return file_contents

def read_item(item):
	string_temp = ''
	try :
		string_temp = config.get('info',item)
	except : 
#		print "get config item error"
		return (0,"get item error")
	else :
		if len(string_temp) :
			return (1,string_temp)
		else : 
#			print "get item is null"
			return (0,"get item is null")

def read_config():
	global config
	global CONFIG_VERSION
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
	global dispense_flags
	global download_temp_bugid
	global download_temp_bug_path
	get_item_ret = []
	config=ConfigParser.ConfigParser() 
	with open('./config','rw') as configfd: 
		config.readfp(configfd)

	get_item_ret = read_item('CONFIG_VERSION')
	if get_item_ret[0] :
		if CONFIG_VERSION == float('%.2f' % float(get_item_ret[1])) :
			return
		CONFIG_VERSION = float('%.2f' % float(get_item_ret[1]))
		print 'config cersion : V%.2f ' % CONFIG_VERSION
	else : 
		print "get config version error"
		return

	get_item_ret = read_item('BUGZILLA_USERNAME')
	if get_item_ret[0] :
		BUGZILLA_USERNAME = get_item_ret[1]
		print 'BUGZILLA_USERNAME = %s ' % BUGZILLA_USERNAME

	get_item_ret = read_item('BUGZILLA_PASSWORD')
	if get_item_ret[0] :
		BUGZILLA_PASSWORD = get_item_ret[1]
		print 'BUGZILLA_PASSWORD = %s ' % BUGZILLA_PASSWORD

	get_item_ret = read_item('KERNEL_MEMBERS')
	if get_item_ret[0] :
		KERNEL_MEMBERS = get_item_ret[1].split(',')
		print 'KERNEL_MEMBERS = %s ' % KERNEL_MEMBERS

	get_item_ret = read_item('SEND_MAIL')
	if get_item_ret[0] :
		SEND_MAIL_ADDRESS = get_item_ret[1].split(',')
		print 'SEND_MAIL_ADDRESS =  %s ' % SEND_MAIL_ADDRESS

	get_item_ret = read_item('STATUS_FIELDS')
	if get_item_ret[0] :
		STATUS_FIELDS = get_item_ret[1].split(',')
		print 'STATUS_FIELDS =  %s ' % STATUS_FIELDS

	get_item_ret = read_item('PRODUCT_FIELDS')
	if get_item_ret[0] :
		PRODUCT_FIELDS = get_item_ret[1].split(',')
		print 'PRODUCT_FIELDS =  %s ' % PRODUCT_FIELDS

	get_item_ret = read_item('DEFAULT_FIELDS')
	if get_item_ret[0] :
		DEFAULT_FIELDS = get_item_ret[1].split(',')
		print 'DEFAULT_FIELDS =  %s ' % DEFAULT_FIELDS

	get_item_ret = read_item('FTP_NAME')
	if get_item_ret[0] :
		FTP_NAME = get_item_ret[1]
		print 'FTP_NAME = %s ' % FTP_NAME
	get_item_ret = read_item('FTP_PASSWORD')
	if get_item_ret[0] :
		FTP_PASSWORD = get_item_ret[1]
		print 'FTP_PASSWORD = %s ' % FTP_PASSWORD

	get_item_ret = read_item('SAMBA_USERNAME')
	if get_item_ret[0] :
		SAMBA_USERNAME = get_item_ret[1]
		print 'SAMBA_USERNAME = %s ' % SAMBA_USERNAME
	get_item_ret = read_item('SAMBA_PASSWORD')
	if get_item_ret[0] :
		SAMBA_PASSWORD = get_item_ret[1]
		print 'SAMBA_PASSWORD = %s ' % SAMBA_PASSWORD
	get_item_ret = read_item('SAMBA_REMOTEIP')
	if get_item_ret[0] :
		SAMBA_REMOTEIP = get_item_ret[1]
		print 'SAMBA_REMOTEIP = %s ' % SAMBA_REMOTEIP
	
	get_item_ret = read_item('DISPENSE_FLAG')
	if get_item_ret[0] :
		dispense_flags = int(get_item_ret[1])
		print 'DISPENSE_FLAG = %d ' % dispense_flags

	get_item_ret = read_item('TEST_BUGLIST')
	if get_item_ret[0] :
		TEST_BUGLIST = get_item_ret[1].split(',')
		print 'TEST_BUGLIST = %s ' % TEST_BUGLIST

def snapshot():
	file_contents = ''
	email_contents = ''
	emaili_download_ok_msg = ''
	bugs_sum_table = []
	manipulating_download_buglist = []
	manipulating_bugid_info = []
	global current_bug_all
	global kernel_group_buglist_old
	global kernel_group_buglist_now
	global kernel_group_buglist_new
	global main_save_path 
	global download_bug_list_temp
	global download_temp_bugid
	global download_temp_bug_path

	read_config()

	print "\nnow time : %s " % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	#get main path
#	main_save_path = os.path.split(os.path.abspath(""))[0]
#	print "main path : %s " % main_save_path
	
	api = API('http://bugzilla.spreadtrum.com/bugzilla', 'False', 'None', 'None')
	ret = api.login(BUGZILLA_USERNAME, BUGZILLA_PASSWORD)
	if not ret:
		print "snapshot : %s :Login  ok !" % BUGZILLA_USERNAME
		pass
	else:
		print "Log in error !"
	#test download bug
#	download_buglist_test = ['746973']
#	print download_buglist_test
#	print download_buglist_test
	#test ftp down log
#	get_sysdump(r'ftp://ftp.spreadtrum.com/Testlogs/PSST/AndroidN/iWhale2/MOCORDROID7.0_Trunk_K44_IWHALE2_W17.27.5/704315_017.rar')
#	print '-----------------------------guhewei : 727619----------------------------'
#	get_bug_files(api,727619)
#	print '-----------------------------gaoshuai : 738276----------------------------'
#	get_bug_files(api,738276)
#	print '----------------------------Arvid Chang : 727619----------------------------'
#	get_bug_files(api,736380)
#	print '-----------------------------qian ji : 737832----------------------------'
#	get_bug_files(api,737832)
#	print '-----------------------------pu xu : 737797----------------------------'
#	get_bug_files(api,737797)
#	print '-----------------------------zhaoyang : 738373----------------------------'
#	get_bug_files(api,738373)
#	print '-----------------------------qian ji : 738266----------------------------'
#	get_bug_files(api,738266)
#	print '-----------------------------liyan : 738941----------------------------'
#	get_bug_files(api,738941)
#	print '-----------------------------hui_hui.zhang : 739513----------------------------'
#	get_bug_files(api,739513)
#	print '-----------------------------jiaqi.chen : 741537----------------------------'
#	get_bug_files(api,741537)
#	print '-----------------------------Peng_peng.Li : 741351----------------------------'
#	get_bug_files(api,741351)
#	get_bug_files(api,745160)
#	get_bug_files(api,745163)
#	get_bug_id_info(api,'745160')

	#mytest(api,668507)	
	#	save bugs info to /home/apuser/Downloads/bugs	
	current_bug_all = get_kernel_bug_all(api)
	bugs_sum_table = make_bugs_table_contents(current_bug_all)
	kernel_group_buglist_now = get_bug_id_list(current_bug_all)
	temp_string = bug_id_list_read(main_save_path,'kernel_bug_info')

	#download config bug id
	if len(TEST_BUGLIST) :
		downloadlog(api,TEST_BUGLIST)
	if os.path.exists(main_save_path+ "/manu_buglist") :
		manipulating_download_buglist = bug_info_read_line(main_save_path, "manu_buglist")
	if len(manipulating_download_buglist):
		bug_info_save_write(main_save_path, "manu_buglist", "") 
		for x in manipulating_download_buglist:
			if ',' in x :
#				print "manipulating download bug info %s" % x
				if '\n' in x:
					x = x.replace("\n", "")
#					print "path : %s" % x 
				manipulating_bugid_info = x.split(',')
				kernel_group_buglist_new.append(manipulating_bugid_info[0])
				get_sysdump(manipulating_bugid_info[0], manipulating_bugid_info[1])
				manipulating_bugid_info = []
		kernel_group_buglist_new = []

	#get old bugid in kernel_group_buglist_old
	if len(temp_string) > 0 :
		kernel_group_buglist_old = temp_string[:temp_string.index(']')].strip('[').replace('\'','').replace(' ','').split(',')
	#print "old buglist %s " %  kernel_group_buglist_old
	#add bug to buglist_new	
	for x in kernel_group_buglist_now:
		if x not in kernel_group_buglist_old:
			kernel_group_buglist_new.append(x)
	#delete bug from buglist_old
#	for x in kernel_group_buglist_old:
#		if x in kernel_group_buglist_now:
#			kernel_group_buglist_old.pop(kernel_group_buglist_old.index(x))
	#print 'new bug list:%s' % kernel_group_buglist_new
	#show_bugs_table(bugs_sum_table)
	time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	f_time_line = time_now + '\n'
	file_contents = f_time_line +'Current bugs:\n'
	file_contents += save_bugs_table(bugs_sum_table)
	file_contents += "\n\nKernel group all bugs (Total %s):\nbugid : %s\n" % (len(kernel_group_buglist_now),kernel_group_buglist_now)
	file_contents += get_bugs_info_str(current_bug_all)
	bug_info_save_write(main_save_path,'kernel_bug_info', file_contents)

	#print bug_info_read(BUGINFO_SAVE) 
	
	#	show bugs info to kernel members by email
	#add bug send mail to fanlc
	if len(kernel_group_buglist_new) > 0 :
		email_msg = email_html_table(bugs_sum_table)
		email_msg = email_msg + "\n\nKernel group all bugs (Total %s):\n%s\n" % (len(kernel_group_buglist_now),kernel_group_buglist_now)
		email_msg = email_msg + "kernel group handle bug:%s \nkernel group increase bug:%s \n\n\n" % (len(kernel_group_buglist_old) + len(kernel_group_buglist_new) - len(kernel_group_buglist_now),len(kernel_group_buglist_new))
		email_msg = email_msg.replace('\n','<br>')
		email_msg = email_msg +  email_html_table_bug_detail(current_bug_all)
		send_email(email_msg,'fanlc@spreadst.com')
		print "send email to fanlc@spreadst.com !"
		#send_email(email_msg,'system_stability1@spreadst.com')

	#downloads bug log	
	if len(kernel_group_buglist_new) > 0:
		downloadlog(api,kernel_group_buglist_new)
	elif len(download_timeout_buglist) > 0:
		downloadlog(api,download_timeout_buglist)
	elif len(no_file_buglist) > 0:
		downloadlog(api,no_file_buglist)
	elif socket_server.socket_link_num_flag == 0:
		if len(download_bug_list_dispense) > 0:
			downloadlog(api,download_bug_list_dispense)

	for x in download_bug_list_temp:
		if x in kernel_group_buglist_new :
			kernel_group_buglist_new.pop(kernel_group_buglist_new.index(x))

	if len(socket_server.download_ok_list) > 0 :
		for x in socket_server.download_ok_list :
			if x in download_bug_list_dispense:
				download_bug_list_dispense.pop(download_bug_list_dispense.index(x))
		emaili_download_ok_msg = email_html_table_download_ok_bug(current_bug_all)
		
		for x in SEND_MAIL_ADDRESS :
			send_email(emaili_download_ok_msg,x)
			pass
#	print 'logout'
	api.logout()
	print '------------------------------end---------------------------------'


def periodicity_main_task():
	file_contents = ''
	email_contents = ''
	#	save bugs info to ~/Downloads/bugs/	
	bugs_table_init()
	current_bug_all = get_kernel_bug_all(bugzilla_api)




bugzilla_api = API('http://bugzilla.spreadtrum.com/bugzilla', 'False', 'None', 'None')


def periodicity():
	global socket
	global main_save_path
#	ret = bugzilla_api.login('fanlc@spreadst.com', 'f1111111')
#	if not ret:
#		print "periodicity : fanlc:Login  ok !"
#		pass
#	else:
#		print "Log in error !"
	#delay run snapshot 5min
	socket = socket_server.MySocket(main_save_path)
	timming_exe(5*60)
#	bugzilla_api.logout()


	

if __name__ == '__main__':
#	snapshot()
#	global main_save_path
	main_save_path =os.path.split(os.path.split(sys.argv[0])[0])[0]
	print "main save path %s " % main_save_path
	periodicity()
	#timming_exe(3*3600)
