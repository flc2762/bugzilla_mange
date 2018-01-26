#-*- coding:utf-8 -*-

import socket
import sys
import multiprocessing
import threading
from myftp import MyFTP
import pexpect
import os
import time

download_log_list = []

socket_link = ''
FTP_IP = "ftp.spreadtrum.com"
TCP_SERVER_IP = '10.0.70.50'
TCP_PORT = 1234
RECV_SIZE = 1024

ssh_ip = '10.0.70.41'
ssh_port = 22
ssh_user = 'apuser'
ssh_password = '123456'
ssh_remote_path_dir = '/home/apuser/bug_work/buglist/'

main_path = ''
code_dir = 'apply-v4.0'
SAVE_DOWNLOAD_LOG_STATUS = '.socketclientlog'

def ssh_exec_scp(dst_file, src_file):
	for x in range(3,13) :
		try :
			scp_command=pexpect.spawn('/usr/bin/scp -r ' + src_file + ' ' + dst_file, timeout = x*100)
			expect_result = scp_command.expect([r'assword:',r'yes/no'],timeout = 300)
			if expect_result == 0:
				print "0 scp file : %s to %s... " % (src_file, dst_file)
				scp_command.sendline(ssh_password)
				scp_command.read()
			elif expect_result == 1:
				print "1 scp file : %s to %s... " % (src_file, dst_file)
				scp_command.sendline('yes')
				scp_command.expect('assword:',timeout = 300)
				scp_command.sendline(ssh_password)
				scp_command.read()
		except Exception, e :
			print "ssh scp file error %d:%s" % (x,e)
		else : 
			print "ssh scp file ok"
			return 1
	return 0

def scp_file_to_server(bugid, filename, index):
	global main_path
	localfilepath = main_path + r'/' + str(bugid) + r'/' + str(index) +  '_' + filename
	remotefilepath = ssh_remote_path_dir + str(bugid) + r'/' + str(index) + '_' + filename
	if ssh_exec_scp('apuser@' + ssh_ip + ':' + remotefilepath, localfilepath) :
		os.remove(localfilepath)
		return 1
	else : 
		return 0
	

def client_send(sock, data):
	sock.send(data)

def client_recv(sock):
	return sock.recv(RECV_SIZE)

def ftp_download_log(bugid, ftp_filepath, ftp_filestart, ftp_filesize, ftp_username, ftp_password, ftp_index):
	global socket_link
        global main_path
	download_status = [0, ""]
	num = 0
	ftp = MyFTP(1,main_path)
	filename = ftp_filepath.split('/')[-1]
	if FTP_IP in ftp_filepath :
		filepath_dir = ftp_filepath[ftp_filepath.index(FTP_IP) + len(FTP_IP):ftp_filepath.index(filename)]
	else :
		filepath_dir = ftp_filepath[0:ftp_filepath.index(filename)]
	while download_status[0] == 0 and num < 10000 :
		download_status = ftp.download_part_log(FTP_IP, 21, ftp_username, ftp_password, bugid, filepath_dir, filename, ftp_filestart, ftp_filesize,  ftp_index)
		num += 1 
#	print "download %d is %s" % (num, download_status)
	if download_status[0]:
		#download file send to server
		if scp_file_to_server(bugid, filename, ftp_index) :
			client_send(socket_link, "downloadok:filepath:" + ftp_filepath + ";bugid:" + str(bugid) + ";index:" + str(ftp_index))
			print 'send download ok to %s ' % socket_link
                        logwrite = open(main_path + r'/' + SAVE_DOWNLOAD_LOG_STATUS,'ab')
                        logwrite.write("download bugid " + str(bugid) + ' index ' + str(ftp_index) + " ok send to " + str(socket_link))
			logwrite.close()
		else :
			print "scp file to server error" 
	else :
		print "download %s index %s error " % (str(bugid),str(ftp_index))

def handle_client_recvdata(data):
	cut_data = []
        global main_path
        global socket_link
	global code_path
	print "recv server data %s " % data
        logwrite = open(main_path + r'/' + SAVE_DOWNLOAD_LOG_STATUS,'ab')
        logwrite.write("recv server data " + data + '\n')
	logwrite.close()
	if "downloadlog:" in data :
		cut_data = data[12:].split(';')
		for x in cut_data:
			if 'bugid:' in x:
				bugid = int(x.split(':')[1])
			elif 'filepath:' in x:
				ftp_filepath = x[9:]
			elif 'start:' in x:
				ftp_filestart = int(x.split(':')[1])
			elif 'size:' in x:
				ftp_filesize = int(x.split(':')[1])
			elif 'username:' in x:
				ftp_username = x.split(':')[1]
			elif 'password:' in x:
				ftp_password = x.split(':')[1]
			elif 'index:' in x:
				ftp_index = int(x.split(':')[1])
		print (bugid, ftp_filepath, ftp_filestart, ftp_filesize, ftp_username, ftp_password, ftp_index)
		
		ftp_download_bug_log = threading.Thread(target = ftp_download_log,args=(bugid, ftp_filepath, ftp_filestart, ftp_filesize, ftp_username, ftp_password, ftp_index), name = 'ftp_download_log')
		ftp_download_bug_log.start()
	elif "updatecode" in data :
            if ssh_exec_scp(main_path, 'apuser@' + ssh_ip + ':' + ssh_remote_path_dir + code_dir) :
                client_send(socket_link, "updatecodeok:" + socket_link)
                socket_link.close()
                cur_pid = os.getpid()
                print "update code ok"
                os.system("/usr/bin/python " + code_path + " &")
                os.system("sudo kill -9 " + str(cur_pid))
		
		
def client_link():
	global socket_link
        global main_path
#        main_path = os.path.split(os.path.abspath(""))[0]
	while True :
		while True :
			try :
				socket_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				socket_link.connect((TCP_SERVER_IP, TCP_PORT))
			except Exception, e :
				print "link socket server error %s" % e
				socket_link.close()
			else :
				break
			time.sleep(30)
		print "connet ok %s " % socket_link
                logwrite = open(main_path + r'/' + SAVE_DOWNLOAD_LOG_STATUS,'ab')
                logwrite.write('connet ok ' + str(socket_link) + '\n')
		logwrite.close()
		while True :
			try :
				data = client_recv(socket_link)
				if not data :
					break
				handle_client_recvdata(data)
			except Exception, e :
				print "socket client recv data error %s" % e
				break
#		socket_link.send(b'exit')
		socket_link.close()

if __name__ == '__main__':
#	global main_path
	code_path = sys.argv[0]
	main_path = os.path.split(os.path.split(sys.argv[0])[0])[0]
        print "code_path %s " % code_path
	print "main path %s " % main_path
	client_link()
