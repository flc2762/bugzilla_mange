#!/usr/bin/python
#encoding=utf-8

import os
import sys
import time
import print_info
import socket
import threading
import multiprocessing
import getpass
import dispense_work

class socket_server():

    socket_client_list = []
#    socket_client_close_list = []
    socket_client_list_lock = threading.Lock()
#    socket_client_close_list_lock = threading.Lock()
    dispense_work_list = []
    redispense_work_list = []
    dispense_work_list_lock = threading.Lock()
    download_log_ok_list = []
    download_log_ok_list_lock = threading.Lock()
    bugid_max_index = []
    bugid_max_index_lock = threading.Lock()
    server_main_path = ''
    socket_server_proc = 0
    socket_recv_data_remnant = ''
    update_code = 0
    update_code_addr_list = []
    update_code_addr_list_lock = threading.Lock()

    def __init__(self, ip, port, recv_size, connect_num):
        self.socket_server_ip = ip
        self.socket_server_port = port
        self.socket_server_size = recv_size
        self.socket_server_conn_num = connect_num

        if self.socket_server_proc == 0:
            self.socket_server_proc = threading.Thread(target=self.socket_server_thread, name = 'socket_server_proc')
            self.socket_server_proc.start()

    def join_bug_log_file(self, bugid, path, file_name, max_index):

        local_file_dir = ''
        local_file_dir = path + r'/' + str(bugid)

        local_file_name = file_name

        print_string = "join bug %s file %s log ..." % (str(bugid), local_file_name)
        print_info.print_info(print_info.PRINT_INFO, print_string)
        if os.path.exists(local_file_dir + r'/' + local_file_name):
            os.remove(local_file_dir + r'/' + local_file_name)
        for x in range(max_index + 1):
            try:
                fread = open(local_file_dir + r'/' + str(x) + '_' + local_file_name, 'r')
            except Exception, e:
                print_string = "join bug %s file error,open file %s" % (str(bugid), e)
                print_info.print_info(print_info.PRINT_ERROR, print_string)
            else:
                data = fread.read()
                with open(local_file_dir + r'/' + local_file_name, 'ab') as lwrite:
                    lwrite.write(data)
                fread.close()
                os.remove(local_file_dir + r'/' + str(x) + '_' + local_file_name)

        self.download_log_ok_list_lock.acquire()
        self.download_log_ok_list.append(bugid)
        self.download_log_ok_list_lock.release()

        print_string = "join bug %s file %s ok" % (str(bugid), local_file_name)
        print_info.print_info(print_info.PRINT_INFO, print_string)

    def socket_server_send(self, sock, data):
        try:
            sock.send(data)
        except Exception, e:
            print_string = "send data to socket %s ,client error %s" % (sock, e)
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            return 0
        else :
            return 1

    def socket_server_recv(self, sock):
        return sock.recv(self.socket_server_size)

    def handle_recv_data(self, sock, addr, data):
        cut_data = []
        max_index_num = 0
        max_index = 0
        download_ok_bugid = ''
        download_ok_index = 0
        download_ok_filename = ''
        list_index = 0

        print_string = "recv data %s " % data
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

        if len(self.socket_recv_data_remnant):
            data = self.socket_recv_data_remnant + data
            self.socket_recv_data_remnant = ''

        if '*' in data:
            cut_data = data.strip('*').split('*')
            if data[-1] != '*':
                self.socket_recv_data_remnant = cut_data[-1]
                cut_data.pop(-1)
        else:
            if not data or data.decode('utf-8') == 'exit':
                sock.close()
                self.socket_client_list_lock.acquire()
                for x in self.socket_client_list:
                    if sock in x:
                        self.socket_client_list.pop(self.socket_client_list.index(x))
                        break
                self.socket_client_list_lock.release()

                if len(self.dispense_work_list):
                    print_string = 'dispense_work_list %s' % self.dispense_work_list
                    print_info.print_info(print_info.PRINT_INFO, print_string)
                    self.dispense_work_list_lock.acquire()
                    for i in range(len(self.dispense_work_list) - 1, -1, -1):
                        if sock in self.dispense_work_list[i]:
                            self.redispense_work_list.append(self.dispense_work_list[i])
                            self.dispense_work_list.pop(i)
                    self.dispense_work_list_lock.release()
            self.socket_recv_data_remnant += data
            return 0

        print_string = "server socket recv data %s " % cut_data
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

        for recv_data_per in cut_data :
            if "username" in recv_data_per :
                if ':' in recv_data_per:
                    cut_data_per = recv_data_per.split(':')
                    self.socket_client_list_lock.acquire()
                    for x in self.socket_client_list:
                        if sock in x and addr in x:
                            self.socket_client_list[self.socket_client_list.index(x)][2] = cut_data_per[1]
                            print_string = "client socket info(username) %s " % self.socket_client_list[
                                self.socket_client_list.index(x)]
                            print_info.print_info(print_info.PRINT_DEBUG, print_string)
                    self.socket_client_list_lock.release()

            elif "ftpspeed" in recv_data_per :
                if ':' in recv_data_per:
                    cut_data_per = recv_data_per.split(':')
                    self.socket_client_list_lock.acquire()
                    for x in self.socket_client_list:
                        if sock in x:
                            self.socket_client_list[self.socket_client_list.index(x)][3] = int(cut_data_per[1])
                            self.socket_client_list.sort(reverse=True, key=lambda x: x[3])
                            print_string = "client socket info(speed) %s " % self.socket_client_list[self.socket_client_list.index(x)]
                            print_info.print_info(print_info.PRINT_DEBUG, print_string)
                            break
                    self.socket_client_list_lock.release()
            elif 'downloadok:' in recv_data_per :
                cut_data_per = recv_data_per[len('downloadok:'):].split(';')
                for x in cut_data_per:
                    if 'bugid:' in x:
                        download_ok_bugid = x.split(':')[1]
                    if 'index:' in x:
                        download_ok_index = int(x.split(':')[1])
                    if 'filename:' in x:
                        download_ok_filename = x.split(':')[1]
                if len(self.bugid_max_index):
                    for x in self.bugid_max_index:
                        if download_ok_bugid in x:
                            if x[1] < download_ok_index:
                                self.bugid_max_index_lock.acquire()
                                self.bugid_max_index[self.bugid_max_index.index(x)][1] = download_ok_index
                                max_index = download_ok_index
                                self.bugid_max_index_lock.release()
                            else:
                                max_index = x[1]
                            break
                        else:
                            max_index_num += 1
                    if max_index_num == len(self.bugid_max_index):
                        self.bugid_max_index_lock.acquire()
                        self.bugid_max_index.append([download_ok_bugid, download_ok_index])
                        max_index = download_ok_index
                        self.bugid_max_index_lock.release()
                    max_index_num = 0
                else:
                    self.bugid_max_index_lock.acquire()
                    self.bugid_max_index.append([download_ok_bugid, download_ok_index])
                    max_index = download_ok_index
                    self.bugid_max_index_lock.release()

                self.dispense_work_list_lock.acquire()
                for x in self.dispense_work_list:
                    if download_ok_bugid in x and download_ok_index in x:
                        self.dispense_work_list.pop(self.dispense_work_list.index(x))
                self.dispense_work_list_lock.release()

                self.dispense_work_list_lock.acquire()
                list_index = 0
                for y in range(len(self.dispense_work_list) - 1, -1, -1):
                    if download_ok_bugid in self.dispense_work_list[y]:
                        list_index = y + 1
                        break
                if list_index > 0:
                    self.dispense_work_list_lock.release()
                    continue
                list_index = 0
                for y in range(len(self.redispense_work_list) - 1, -1, -1):
                    if download_ok_bugid in self.redispense_work_list[y]:
                        list_index = y + 1
                        break
                if list_index > 0:
                    self.dispense_work_list_lock.release()
                    continue
                self.dispense_work_list_lock.release()

                self.bugid_max_index_lock.acquire()
                self.bugid_max_index.pop(self.bugid_max_index.index([download_ok_bugid, max_index]))
                self.bugid_max_index_lock.release()
                join_bug_log_file_proc = threading.Thread(target=self.join_bug_log_file,
                                                          args=(download_ok_bugid, self.server_main_path,
                                                                download_ok_filename, max_index),
                                                          name="join_bug_log")
                join_bug_log_file_proc.start()
                max_index = 0
            elif 'updatecodeok:' in recv_data_per:
                updatecodeok_socket = recv_data_per.split(':')[1]
                self.update_code_addr_list_lock.acquire()
                for x in self.socket_client_list:
                    if updatecodeok_socket in x:
                        if x[1][0] not in self.update_code_addr_list:
#                            self.update_code_addr_list_lock.acquire()
                            self.update_code_addr_list.append(x[1][0])
#                            self.update_code_addr_list_lock.release()
                        break
                self.update_code_addr_list_lock.release()
                print_string = "update code ok socket %s" % updatecodeok_socket
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
#            elif len(recv_data_per) > 0:
#                self.socket_recv_data_remnant = self.socket_recv_data_remnant + recv_data_per

        return 1

    def socket_server_status(self, sock, addr):
        print_string = 'Accept new connection from %s:%s...' % (addr[0],str(addr[1]))
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
        while True:
            recv_data = self.socket_server_recv(sock)
            if not self.handle_recv_data(sock, addr, recv_data):
                break
        print_string = "close connection from %s:%s..." % addr
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

    def socket_server_thread(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #set SO_REUSEADDR is true
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind
        s.bind((self.socket_server_ip, self.socket_server_port))
        s.listen(self.socket_server_conn_num)
        print_info.print_info(print_info.PRINT_INFO, 'Socket server waiting for connection...')
        while True:
            sock, addr = s.accept()
            print_string = 'socket sock %s; addr %s' % (sock, addr)
            print_info.print_info(print_info.PRINT_DEBUG, print_string)


            t = threading.Thread(target=self.socket_server_status, args=(sock, addr), name="socket_master")
            t.start()

            self.socket_client_list_lock.acquire()
            self.socket_client_list.append([sock, addr, '', 100000])
            self.socket_server_send(sock, 'getusername*')
            self.socket_server_send(sock, 'getftpspeed*')
            self.socket_client_list_lock.release()

            if self.update_code:
                if addr[0] not in self.update_code_addr_list:
                    self.socket_server_send(sock, 'updatecode*')
                    self.update_code_addr_list_lock.acquire()
                    self.update_code_addr_list.append(addr[0])
                    self.update_code_addr_list_lock.release()
                    print_string = 'send updatecode to sock :%s' % sock
                    print_info.print_info(print_info.PRINT_DEBUG, print_string)

        print_info.print_info(print_info.PRINT_DEBUG, 'socket sock server end')

if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
    socket_server_fd = socket_server('10.0.70.50', 1024, 1024, 50)
    while True:
        if len(socket_server_fd.socket_client_list) :
            socket_server_fd.socket_server_send(socket_server_fd.socket_client_list[0][0], 'getusername*')
            socket_server_fd.socket_server_send(socket_server_fd.socket_client_list[0][0], 'getftpspeed*')
            time.sleep(5)
            break