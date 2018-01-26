#-*- coding:utf-8 -*-
import threading
import sys
import multiprocessing
import socket
import time
import os
#import kernel_bugs

bugid = 748921
downloadpath = 'ftp://ftp.spreadtrum.com/TestLogs/PSST/AndroidN/iSharkL2/MOCORDROID7.0_Trunk_K44_ISharkL2_CMCC_W17.36.5/748921.rar'
filesize = 550012972

FTP_NAME = "spreadst"
FTP_PASSWORD = "spread$26?ST"

TCP_SERVER_IP = '10.0.70.17'
TCP_PORT = 1234
RECV_SIZE = 1024

connect_list = []
download_bug_list = [] 
dispense_bug_list = []
wait_download_bug_list = []
download_ok_list = []
max_index = []
socket_server_proc = 0
socket_link_num_flag = 1
main_path = ''

class MySocket():
	def __init__(self,path):
		global socket_server_proc
		global main_path
		main_path = path
#		download_bug_list.append([bugid, downloadpath, filesize])
#		print "bug list %s " % download_bug_list
#		download_bug_log_proc = threading.Thread(target = self.download_bug, name = 'download_bug')
#		download_bug_log_proc.start()
		if socket_server_proc == 0:
			socket_server_proc = threading.Thread(target = self.socket_server, name = 'socket_server_proc')
			socket_server_proc.start()

	def join_bug_log_file(self, bugid, filepath, max_index):
		global download_ok_list
		global main_path
		local_file_dir = ''
		local_file_dir = main_path + r'/' + str(bugid)
		local_file_name = filepath.split('/')[-1]
		print "join bug %s file log ..." % str(bugid)
		if os.path.exists(local_file_dir + r'/' + local_file_name):
			os.remove(local_file_dir + r'/' + local_file_name)
		for x in range(max_index + 1):
			fread = open(local_file_dir + r'/' + str(x) + '_' + local_file_name, 'r')
			data = fread.read()
			with open(local_file_dir + r'/' + local_file_name,'ab') as lwrite:
				lwrite.write(data)
			fread.close()
			os.remove(local_file_dir + r'/' + str(x) + '_' + local_file_name)
		f = open(main_path + r'/bug_id_statistics','ab')
		f.write('download bug id log ' + str(bugid) + ' end\n')
		f.close()
		download_ok_list.append(bugid)
		print "join bug %s file log ok" % str(bugid)

	def tcplink_send(self, sock, data):
		try :
			sock.send(data)
		except :
			return 0
		else :
			return 1

	def tcplink_recv(self, sock, addr):
		return sock.recv(RECV_SIZE)

	def handle_recv_data(self, sock, addr, recv_data):
		global connect_list
		global dispense_bug_list
		global max_index
		global socket_link_num_flag
		temp_bug_id_flag = 1
		cut_data = []
		bugid = 0
		filepath = ''
		max_index_num = 0
		temp_max_index = 0
		if not recv_data or recv_data.decode('utf-8') == 'exit':
			sock.close()
                        self.tcplink_send(sock,"close sock send data ")
                        print "send data to close sock"
			connect_list.pop(connect_list.index([sock, addr]))
			if len(connect_list)  :
				if temp_bug_id_flag :
					for x in connect_list :
						for y in dispense_bug_list :
							if sock in y:
								print "redispense bug list %s" % y
								send_data_temp = ''
								send_data_temp = 'downloadlog:bugid:' + str(y[1]) + ';filepath:' + y[2] + ';start:' + str(y[3]) + ';size:' + str(y[4]) + ';username:' + y[5] + ';password:' + y[6] + ';index:' + str(y[7]) 
								temp_bug_id_flag = 1
								if self.tcplink_send(x[0],send_data_temp) :
									dispense_bug_list.append([x[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7]])
									dispense_bug_list.pop(dispense_bug_list.index(y))
									break
							else : 
								temp_bug_id_flag = 0
			else :
				dispense_bug_list = []
				socket_link_num_flag = 0
			return 0
		else : 
			print "recv data %s " % recv_data
			if "downloadok:" in recv_data :
				cut_data = recv_data[11:].split(';')
				for x in dispense_bug_list:
					if cut_data[0][9:] in x and cut_data[1].split(':')[-1] in x and int(cut_data[2].split(':')[-1]) ==  x[-1] :
						print "dispense bug list x %s" % x 
						bugid = x[1]
						filepath = x[2]
						if len(max_index) :
							for y in max_index:
								if cut_data[1].split(':')[-1] in y:
									if y[-1] < x[-1] :
										y[-1] = x[-1]
										temp_max_index = x[-1]
									else : 
										temp_max_index = y[-1]
								else :
									max_index_num += 1
							if max_index_num == len(max_index) :
								max_index.append([cut_data[1].split(':')[-1],x[-1]])
								temp_max_index = x[-1]
						else :
							max_index.append([cut_data[1].split(':')[-1],x[-1]])
							temp_max_index = x[-1]
						dispense_bug_list.pop(dispense_bug_list.index(x))
				for x in dispense_bug_list:
					if cut_data[0][9:] in x :
						return 1
				max_index.pop(max_index.index([cut_data[1].split(':')[-1],temp_max_index]))
				join_bug_file = threading.Thread(target=self.join_bug_log_file, args=(bugid, filepath, temp_max_index), name = "join_bug")
				join_bug_file.start() 
			return 1

	def tcplink_status(self, sock, addr):
		print('Accept new connection from %s:%s...' % addr)
		while True :
			recv_data = self.tcplink_recv(sock, addr)
			if not self.handle_recv_data(sock, addr, recv_data):
				break
		print "close connection from %s:%s..." % addr
	
	def socket_server(self):
		global connect_list
		global download_bug_list
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#bind 
		s.bind((TCP_SERVER_IP, TCP_PORT))
		s.listen(50)
		print('Waiting for connection...')
		while True:
			sock, addr = s.accept()
			connect_list.append([sock, addr])
			t = threading.Thread(target=self.tcplink_status, args=(sock, addr), name = "socket_master")
#			download_bug_list.append([bugid, downloadpath, filesize])
#			print "bug list %s " % download_bug_list
			t.start()

	def dispense_download_log(self, download_bug_info):
		global dispense_bug_list
		global download_bug_list
		global connect_list
		filesize_temp = download_bug_info[2]
		dispense_block_num = 0
		if len(connect_list) :
			dispense_block_size = (filesize_temp + len(connect_list))/ len(connect_list)
		else :			
			return 0
 		download_size = dispense_block_size
	
		while filesize_temp > 0:
			for x in connect_list:
				send_data_temp = ''
				if filesize_temp < dispense_block_size:
					download_size = filesize_temp
				print "sock : %s" % x
				send_data_temp = 'downloadlog:bugid:' + str(download_bug_info[0]) + ';filepath:' + download_bug_info[1] + ';start:' + str(dispense_block_num*dispense_block_size) + ';size:' + str(download_size) + ';username:' + FTP_NAME + ';password:' + FTP_PASSWORD + ';index:' + str(dispense_block_num)
				if self.tcplink_send(x[0],send_data_temp) :
					dispense_bug_list.append([x[0], download_bug_info[0], download_bug_info[1], dispense_block_num*dispense_block_size, download_size, FTP_NAME, FTP_PASSWORD, dispense_block_num])
					filesize_temp = filesize_temp - download_size
					if filesize_temp == 0 :
						break
					dispense_block_num += 1
		if download_bug_info in download_bug_list:
			download_bug_list.pop(download_bug_list.index(download_bug_info))
			print "now download bug list %s " % download_bug_list
				
	def download_bug(self):
		#get bug path
		#periodicity()
		global download_bug_list
		global connect_list
		while True:
			print "dispense bug to client..."
			if len(download_bug_list) > 0 :
				for x in download_bug_list :
					if len(connect_list) > 0 : 
						self.dispense_download_log(x)
					else :
						#download log self
						pass
			print "wait link...."
			time.sleep(30)
		print 'close thread download '

if __name__ == '__main__':
        main_path = os.path.split(os.path.split(sys.argv[0])[0])[0]
	a = MySocket(main_path)
