#!/usr/bin/python
#encoding=utf-8

from ftplib import FTP   
import sys    
import os.path
import socket_server

dispense_flag = 0
socket_link_num = 0
main_path = ''

SAVE_DOWNLOAD_LOG_STATUS = '.downloadlogstatus'

class MyFTP(FTP):
	'''  
	conncet to FTP Server  
	'''    
	def __init__(self,flag,path):
		global main_path
		dispense_flag = flag
		main_path = path
		pass  
#		print 'make a ftp object'  
	def ConnectFTP(self,remoteip,remoteport,loginname,loginpassword):
		global main_path    
		ftp=MyFTP(dispense_flag,main_path)  
		
		# try again 3
		for n in range(3) :
			try: 
				#set 10s timeout 
				ftp.connect(remoteip,remoteport,10)  
#				print 'connect success '  
			except Exception, e:	
				print >> sys.stderr, "conncet failed - %s" % e
			else:    
				try:    
					ftp.login(loginname,loginpassword)    
#					print('login success') 
				except Exception, e:
					print >>sys.stderr, 'login failed - %s' % e
				else:
#					print 'return 1'
					return (1,ftp)
			print 'connect %d' % n
		return (0,'ftp login failed')
   
	def downloadfile(self, ftp, path_dir, remotefilename, bugid):
		lsize=0L
		fsize=0L
		cmpsize=0
		downloadstatus = 0L
		savelogpath = ''
		global socket_link_num
		global main_path
		try :	
			fsize=ftp.size(remotefilename)
		except :
#			print 'get remote file size error' 
#			ftp.quit()
			return (0,'time out --get file size error')
		else :
			print 'remote file size : %d ' % fsize
		if fsize==0 : # localfime's site is 0
#			ftp.quit()
			return (0,'file size is null')
		#dispense bug to client ,client download part bug 
		elif dispense_flag :
			socket_link_num = len(socket_server.connect_list)
			if socket_link_num > 0:
				socket_server.download_bug_list.append([bugid, path_dir+remotefilename, fsize])
				socket_server.MySocket(main_path).dispense_download_log(socket_server.download_bug_list[0])
				return (1, 'dispense bug to client')
			
		#check local file isn't exists and get the local file size    
#		print str(bugid)
		localfilepath = main_path + r'/' + str(bugid)
#		if not  os.path.exists(localfilepath) :
#			os.mkdir(localfilepath) 
		savelogpath = localfilepath + '/' + SAVE_DOWNLOAD_LOG_STATUS
		localfilepath = localfilepath + r'/' + remotefilename
		print 'localpath : %s' % localfilepath
		if os.path.exists(localfilepath):    
			lsize=os.stat(localfilepath).st_size
			print "local file size %d" % lsize    
		if lsize >= fsize:    
#			print 'local file is bigger or equal remote file'    
#			ftp.quit()
			return (1,'file is download end')
		#save download bug log statistics
#		llogwrite=open(os.path.split(os.path.abspath(""))[0] + r'/' + 'bug_id_statistics','ab')
#		llogwrite.write('download bug id ' + str(bugid) + ' start\n')    
#		llogwrite.close()
		blocksize=1024 * 1024
		cmpsize=lsize
		ftp.voidcmd('TYPE I')
		try :
			conn = ftp.transfercmd('RETR '+remotefilename,lsize)
		except :
#			print 'get file connect error'
			return (0,'time out --get file connect error')
		#lwrite=open(localfilepath,'ab')
		while True:
			try :
				data=conn.recv(blocksize)
			except Exception, e:
#				print "\nrecv data error %s " % e
				#download file error ,remove download file
				#lwrite.close()
				return (0,'time out --get file data error')
			if not data:
#				print '\ndata is null'
				break 
			with open(localfilepath,'ab') as lwrite:
				lwrite.write(data)
#			lwrite.write(data)
			cmpsize+=len(data)
#			logwrite = open(savelogpath,'w')
#			logwrite.write(str(float('%.2f' % (float(cmpsize)/fsize*100))) + '%')
#			logwrite.close()
			with open(savelogpath,'w') as logwrite : 
				logwrite.write(str(float('%.2f' % (float(cmpsize)/fsize*100))) + '%')
			print '\b'*30,'download process:%.2f%%'%(float(cmpsize)/fsize*100),
		print ''
#		lwrite.close()
#		llogwrite=open(os.path.split(os.path.abspath(""))[0] + r'/' + 'bug_id_statistics','ab')
#		if cmpsize >= fsize :
#			llogwrite.write('download bug id ' + str(bugid) + ' end\n')
#		else : 
#			llogwrite.write('download bug id ' + str(bugid) + ' error\n')
#		llogwrite.close()
#		ftp.voidcmd('NOOP')
#		ftp.voidresp()
		try :
			conn.close()
		except :
			pass
#		ftp.quit()
		if cmpsize >= fsize :
			return (1,'download file ok')
		else :
			#download file error ,remove download file
			print "local file size %d ,remote file size %d " % (cmpsize, fsize)
			os.remove(localfilepath)
			return (0,'download file size error')

		
	def download(self,remoteHost,remotePort,loginname,loginpassword,remotePath,bugid):    
#		print 'Try download file'  
#		print 'remotePath : %s' % remotePath  
#		print 'localPath : %s' % localPath  
		#connect to the FTP Server and check the return    
#		remotefileture = 0
		directory = []
		dir_list = []
		remotedirectory = []
		res = self.ConnectFTP(remoteHost,remotePort,loginname,loginpassword)    
		if(res[0]!=1):
			print >>sys.stderr, res[1]
#			sys.exit()
			return (0,res[1])
			
#		print 'ConnectFTP ok'  
		#change the remote directory and get the remote file size    
		ftp=res[1]
		ftp.set_pasv(0)
		dires = self.splitpath(remotePath)
		if dires[0] :
			try :
				ftp.cwd(dires[0]) # change remote work dir 
			except :
#				print "change dir to : %s error" % dires[0]
				return (0,'change dir error')
			else : 
				print 'change dir to : %s' % dires[0]
		remotefile=dires[1]     # remote file name
#		print dires[0]+' '+ dires[1]
#		print 'download remotefile %s' % remotefile
		ret = []
		try :
			dir_list = ftp.nlst()
		except :
			return (0,'time out --get ftp dir error')
		for f in dir_list :
			if remotefile == f:
				print "remote file name :%s" % remotefile
				ret = self.downloadfile(ftp, dires[0], remotefile, bugid)
			elif str(bugid) in f and ".aspx" not in f : 
				remotefile = f
				print "remote file name :%s" % remotefile
				ret = self.downloadfile(ftp, dires[0], remotefile, bugid)
#		print ret
		if ret :
			if 'time out' not in ret[1] :	
#				ftp.voidcmd('NOOP')
#				ftp.voidresp()
				try : 
					ftp.quit()
				except :
					pass
			return ret
		return (0,'not find file')
#			elif remotefile.replace('.rar','.7z') == f :
#				remotefile = remotefile.replace('.rar','.7z')
#				print "remotefile %s" % remotefile
  #                              remotefileture = 1
 #                               break
#			elif remotefile.replace('.rar','.zip') == f :
#				remotefile = remotefile.replace('.rar','.zip')
#				print "remotefile %s" % remotefile
#				remotefileture = 1
#				break
#			else :
#				remotefileture = 0		
#		if not  remotefileture:
#			print "remote does not have the %s" % remotefile
#			return
#		fsize=ftp.size(remotefile)
#		print 'remote file size : %d ' % fsize
#		if fsize==0 : # localfime's site is 0
#			return
			
		#check local file isn't exists and get the local file size    
#		localfilepath = os.path.split(os.path.abspath(""))[0] + r'/' + remotefile
#		print 'localpath : %s' % localfilepath
#		lsize=0L
#		if os.path.exists(localfilepath):    
#			lsize=os.stat(localfilepath).st_size    
#		if lsize >= fsize:    
#			print 'local file is bigger or equal remote file'    
#			return    
#		blocksize=1024 * 1024
#		cmpsize=lsize
#		ftp.voidcmd('TYPE I')
#		conn = ftp.transfercmd('RETR '+remotefile,lsize)
#		lwrite=open(localfilepath,'ab')
#		while True:
#			data=conn.recv(blocksize)
#			if not data:
#				break 
#			lwrite.write(data)
#			cmpsize+=len(data)
#			print '\b'*30,'download process:%.2f%%'%(float(cmpsize)/fsize*100),
#		print ''
#		lwrite.close()
#		ftp.voidcmd('NOOP')
#		ftp.voidresp()
#		conn.close()
#		ftp.quit()

	def download_part_log(self,remoteHost,remotePort,loginname,loginpassword, bugid, path_dir,filename,start,size,index):    
#		print 'Try download file'
		global main_path  
		lsize = 0
		cmpsize = 0
		print 'remotePath : %s' % path_dir
		print 'filename : %s' % filename  
		#connect to the FTP Server and check the return    
		directory = []
		dir_list = []
		remotedirectory = []
                savelogpath = ''
		res = self.ConnectFTP(remoteHost,remotePort,loginname,loginpassword)    
		if(res[0]!=1):
			print >>sys.stderr, res[1]
#			sys.exit()
			return (0,res[1])
			
#		print 'ConnectFTP ok'  
		#change the remote directory and get the remote file size    
		ftp=res[1]
		ftp.set_pasv(0)
		try :
			ftp.cwd(path_dir) # change remote work dir 
		except :
#			print "change dir to : %s error" % dires[0]
			return (0,'part change dir error')
		else : 
			print 'part change dir to : %s' % path_dir
		localfilepath = main_path + r'/' + str(bugid)
		if not  os.path.exists(localfilepath) :
			os.mkdir(localfilepath)
                savelogpath = localfilepath + '/' + SAVE_DOWNLOAD_LOG_STATUS
		localfilepath = localfilepath + r'/' + str(index) + '_' + filename
		if os.path.exists(localfilepath):    
			lsize=os.stat(localfilepath).st_size
			print "part local file size %d" % lsize
		print 'local file path %s ' % localfilepath    
		if lsize >= size:    
			return (1,'part file is download end')
		blocksize=1024 * 1024
		if lsize :
			cmpsize = lsize
		ftp.voidcmd('TYPE I')
		print 'local size %d ; remote size %d ' % (start + lsize, size)
		try :
			conn = ftp.transfercmd('RETR '+ filename,start + lsize)
		except :
#			print 'get file connect error'
			return (0,'time out --part get file connect error')
		#lwrite=open(localfilepath,'ab')
		while True:
			if (size - cmpsize) < blocksize:
				blocksize = size - cmpsize
 
			try :
				data=conn.recv(blocksize)
			except Exception, e:
#				print "\nrecv data error %s " % e
				#download file error ,remove download file
				#lwrite.close()
				return (0,'time out --part get file data error')
			if not data:
#				print '\ndata is null'
				break 
			with open(localfilepath,'ab') as lwrite:
				lwrite.write(data)
#			lwrite.write(data)
			cmpsize+=len(data)
			with open(savelogpath,'w') as logwrite : 
				logwrite.write(str(float('%.2f' % (float(cmpsize)/size*100))) + '%')
			print '\b'*30,'part download process:%.2f%%'%(float(cmpsize)/size*100),
		print ''
		try :
			conn.close()
			ftp.quit()
		except :
			pass
#		ftp.quit()
		if cmpsize >= size :
			return (1,'part download file ok')
		else :
			#download file error ,remove download file
			print "local file size %d ,remote file size %d " % (cmpsize, size)
			os.remove(localfilepath)
			return (0,'part download file size error')
	
	def upload(self,remotehost,remoteport,loginname,loginpassword,remotepath,localpath,callback=None):
		if not os.path.exists(localpath):
			print "Local file doesn't exists"
			return
		self.set_debuglevel(2)
		res=self.ConnectFTP(remotehost,remoteport,loginname,loginpassword)
		if res[0]!=1:
			print res[1]
			sys.exit()
		ftp=res[1]
		remote=self.splitpath(remotepath)
		ftp.cwd(remote[0])
		rsize=0L
		try:
			rsize=ftp.size(remote[1])
		except:
			pass
		if (rsize==None):
			rsize=0L
		lsize=os.stat(localpath).st_size
		print('rsize : %d, lsize : %d' % (rsize, lsize))
		if (rsize==lsize):
			print 'remote filesize is equal with local'
			return
		if (rsize<lsize):
			localf=open(localpath,'rb')
			localf.seek(rsize)
			ftp.voidcmd('TYPE I')
			datasock=''
			esize=''
			try:
				print(remote[1])
				datasock,esize=ftp.ntransfercmd("STOR "+remote[1],rsize)
			except Exception, e:
				print >>sys.stderr, '----------ftp.ntransfercmd-------- : %s' % e
				return
			cmpsize=rsize
			while True:
				buf=localf.read(1024 * 1024)
				if not len(buf):
					print '\rno data break'
					break
				datasock.sendall(buf)
				if callback:
					callback(buf)
				cmpsize+=len(buf)
				print '\b'*30,'uploading %.2f%%'%(float(cmpsize)/lsize*100),
				if cmpsize==lsize:
					print '\rfile size equal break'
					break
			datasock.close()
			print 'close data handle'
			localf.close()
			print 'close local file handle'
			ftp.voidcmd('NOOP')
			print 'keep alive cmd success'
			ftp.voidresp()
			print 'No loop cmd'
			ftp.quit()

	def splitpath(self,remotepath):
		position=remotepath.rfind('/')
		return (remotepath[:position+1],remotepath[position+1:])
	
