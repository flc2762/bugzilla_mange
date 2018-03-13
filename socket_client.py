#!/usr/bin/python
#encoding=utf-8

import os
import sys
import time
import datetime
import print_info
import socket
import threading
import multiprocessing
import getpass
import ftpdownloadfile
import file_ops
from ssh_scp import ssh_scp

socket_client_proc = 0
socket_client_fd = 0
socket_recv_data_remnant = ''
socket_ftp_download_file_speed = 100000

LOG_DIR = 'log'
KERNEL_FILE_NAME_BASE = '.kernel_python_log'
save_log_file_lock = threading.Lock()


class socket_client():
    client_main_path = ''
    scp_server_ip = ''
    scp_user = ''
    scp_password = ''
    scp_dir = ''
    code_path = ''
    def __init__(self, ip, port, recv_size):
        global socket_client_proc
        self.socket_ip = ip
        self.socket_port = port
        self.socket_size = recv_size

        if socket_client_proc == 0:
            socket_client_proc = threading.Thread(target=self.client_link, name='socket_clinet_line_proc')
            socket_client_proc.start()

    def save_log_info_to_file(self, str):
        save_log_file_lock.acquire()
        file_ops.save_append(self.client_main_path + '/' + LOG_DIR, KERNEL_FILE_NAME_BASE +
                             datetime.datetime.now().strftime('%Y-%m-%d'), str)
        save_log_file_lock.release()

    def client_send(self, sock, data):
        try:
            sock.send(data)
        except Exception, e:
            print_string = "send data %s to socket server error %s" % (data, e)
            print_info.print_info(print_info.PRINT_ERROR, print_string)


    def client_recv(self, sock):
        return sock.recv(self.socket_size)

    def ftp_download_log(self, *params):
        ftp_fd = 0
        ret = []
        download_file_num = 0
        local_file_name = ''
        scp_fd = 0

        print_string = "download log params: %s" % str(params)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
        self.save_log_info_to_file(print_string + '\n')
        if len(params) > 9:
            local_file_name = str(params[9]) + '_' + params[6]
            if os.path.exists(self.client_main_path + '/' + str(params[0]) + '/' + local_file_name):
                os.remove(self.client_main_path + '/' + str(params[0]) + '/' + local_file_name)
                print_string = "remove old file,path:%s" % (self.client_main_path + '/' +
                                                        str(params[0]) + '/' + local_file_name)
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
            ftp_fd = ftpdownloadfile.download_ftp(params[1], params[2], params[3], params[4])
            ret = ftp_fd.connect_ftp_server(ftp_fd)
            if ret[0]:
                while download_file_num < 10000:
                    ret = ftp_fd.download_ftp_file_size(ftp_fd, params[5], params[6], self.client_main_path,
                                                        params[0], local_file_name, params[7], params[8])
                    if ret[0]:
                        #update ftp download speed
                        socket_ftp_download_file_speed = ftp_fd.ftp_download_speed
                        scp_fd = ssh_scp(self.scp_server_ip, 22, self.scp_user, self.scp_password,
                                                 self.client_main_path + '/' + str(params[0]),
                                                 self.scp_dir + '/' + str(params[0]))
                        if scp_fd.scp_file_to_dst(local_file_name):
                            self.client_send(socket_client_fd, "downloadok:bugid:" + str(params[0]) +
                                             ";filename:" + params[6] +";index:" + str(params[9]) + '*')
                            os.remove(self.client_main_path + '/' + str(params[0]) + '/' + local_file_name)
                            print_string = "scp file %s to server %s ok" % (local_file_name, self.scp_server_ip)
                            print_info.print_info(print_info.PRINT_DEBUG, print_string)
                            self.save_log_info_to_file(print_string + '\n')
                            print_string = "remove file name %s" % (self.client_main_path + '/' +
                                                                    str(params[0]) + '/' + local_file_name)
                            print_info.print_info(print_info.PRINT_DEBUG, print_string)
                            print_string = "ftp speed %s" % socket_ftp_download_file_speed
                            print_info.print_info(print_info.PRINT_DEBUG, print_string)
                            self.client_send(socket_client_fd, "ftpspeed:" + str(socket_ftp_download_file_speed) + '*')
                        else:
                            print_string = "scp file %s to server %s error" % (local_file_name, self.scp_server_ip)
                            print_info.print_info(print_info.PRINT_DEBUG, print_string)
                        break
                    ftp_fd.ftp_close(ftp_fd)
                    while download_file_num < 10000:
                        time.sleep(30)
                        ftp_fd = ftpdownloadfile.download_ftp(params[1], params[2], params[3], params[4])
                        ret = ftp_fd.connect_ftp_server(ftp_fd)
                        if ret[0]:
                            break
                        download_file_num += 1

    def handle_client_recvdata(self, data):
        global socket_recv_data_remnant
        cut_data = []

        print_string = "resv data len [%d] :%s " % (len(data), data)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

        if len(socket_recv_data_remnant):
            data = socket_recv_data_remnant + data
            socket_recv_data_remnant = ''

        if '*' in data:
            cut_data = data.strip('*').split('*')
            if data[-1] != '*':
                socket_recv_data_remnant = cut_data[-1]
                cut_data.pop(-1)
        else:
            if not data or data.decode('utf-8') == 'exit':
                print_string = "recv exit cmd or link close"
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
            socket_recv_data_remnant += data
            return 0

        print_string = "client socket recv data %s " % cut_data
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

        for recv_data_per in cut_data:
            if 'getusername' in recv_data_per:
                username = getpass.getuser()
                print_string = "user name %s" % username
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
                self.client_send(socket_client_fd, "username:" + username + '*')

            elif 'getftpspeed' in recv_data_per:
                print_string = "ftp speed %s" % socket_ftp_download_file_speed
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
                self.client_send(socket_client_fd, "ftpspeed:" + str(socket_ftp_download_file_speed) + '*')

            elif "downloadlog:" in recv_data_per:
                    cut_data = recv_data_per[len('downloadlog:'):].split(';')
                    for x in cut_data:
                        if 'bugid:' in x:
                            bugid = x.split(':')[1]
                        elif 'ftpserver:' in x:
                            ftp_server = x.split(':')[1]
                        elif 'ftpport:' in x:
                            ftp_port = int(x.split(':')[1])
                        elif 'ftpuser:' in x:
                            ftp_user = x.split(':')[1]
                        elif 'ftppw:' in x:
                            ftp_password = x.split(':')[1]
                        elif 'filepath:' in x:
                            file_path = x.split(':')[1]
                        elif 'filename:' in x:
                            file_name = x.split(':')[1]
                        elif 'start:' in x:
                            ftp_filestart = int(x.split(':')[1])
                        elif 'size:' in x:
                            ftp_filesize = int(x.split(':')[1])
                        elif 'index:' in x:
                            ftp_index = int(x.split(':')[1])
                    ftp_download_bug_log_proc = threading.Thread(target=self.ftp_download_log, args=(
                            bugid, ftp_server, ftp_port, ftp_user, ftp_password, file_path, file_name, ftp_filestart,
                            ftp_filesize, ftp_index), name='ftp_download_log')
                    ftp_download_bug_log_proc.start()

            elif "updatecode" in recv_data_per:
                scp_fd = ssh_scp(self.scp_server_ip, 22, self.scp_user, self.scp_password,
                                         self.client_main_path, self.scp_dir)
                if scp_fd.scp_file_dst_to_local(os.path.split(os.path.split(self.code_path)[0])[1]):
                    #self.client_send(socket_client_fd, "updatecodeok:" + socket_client_fd + '*')
                    cur_pid = os.getpid()
                    print_string = "update code ok, old pid %d" % cur_pid
                    print_info.print_info(print_info.PRINT_DEBUG, print_string)
                    socket_client_fd.close()
                    os.system("/usr/bin/python " + self.code_path + " &")
                    os.system("sudo kill -9 " + str(cur_pid))

#            elif len(recv_data_per) > 0:
#                socket_recv_data_remnant = socket_recv_data_remnant + recv_data_per

        return 1

    def client_link(self):
        global socket_client_fd

        while True:
            # link socket server
            while True:
                try:
                    socket_client_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket_client_fd.connect((self.socket_ip, self.socket_port))
                except Exception, e:
                    print_string = "link socket server error %s" % e
                    print_info.print_info(print_info.PRINT_ERROR, print_string)
                    socket_client_fd.close()
                else:
                    break
                time.sleep(30)
            print_string = "connet socket server ok %s " % socket_client_fd
            print_info.print_info(print_info.PRINT_INFO, print_string)
            self.save_log_info_to_file(print_string + '\n')

            #recv data socket
            while True:
                try:
                    data = self.client_recv(socket_client_fd)
                    if not self.handle_client_recvdata(data):
                        break
                except Exception, e:
                    print_string = "socket client recv data error %s" % e
                    print_info.print_info(print_info.PRINT_ERROR, print_string)
                    break
            try:
#                self.client_send(socket_client_fd, b'exit')
                socket_client_fd.close()
            except Exception, e:
                print_string = "close socket server link error %s" % e
                print_info.print_info(print_info.PRINT_ERROR, print_string)

if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
#    user_name = getpass.getuser()
#    print_string = "get user name  %s" % user_name
#    print_info.print_info(print_info.PRINT_INFO, print_string)

    socket_client_fd = socket_client('10.0.70.50', 1024, 1024)
    socket_client_fd.client_main_path = '/home/local/SPREADTRUM/lc.fan/flc/code/pybz'
    socket_client_fd.scp_server_ip = '10.0.70.50'
    socket_client_fd.scp_user = 'apuser'
    socket_client_fd.scp_password = '123456'
    socket_client_fd.scp_dir = '/home/apuser/Web_Buglist'
    socket_client_fd.code_path = '/home/local/SPREADTRUM/lc.fan/flc/code/pybz'