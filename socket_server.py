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
    socket_client_close_list = []
    socket_client_list_lock = threading.Lock()
    socket_client_close_list_lock = threading.Lock()
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
        if '_' in file_name:
            local_file_name = file_name.split('_')[-1]
        else:
            local_file_name = file_name

        print_string = "join bug %s file %s log ..." % (str(bugid), local_file_name)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
        if os.path.exists(local_file_dir + r'/' + local_file_name):
            os.remove(local_file_dir + r'/' + local_file_name)
        for x in range(max_index + 1):
            fread = open(local_file_dir + r'/' + str(x) + '_' + local_file_name, 'r')
            data = fread.read()
            with open(local_file_dir + r'/' + local_file_name, 'ab') as lwrite:
                lwrite.write(data)
            fread.close()
            os.remove(local_file_dir + r'/' + str(x) + '_' + local_file_name)

        self.download_log_ok_list_lock.acquire()
        self.download_log_ok_list.append(bugid)
        self.download_log_ok_list_lock_lock.release()

        print_string = "join bug %s file %s ok" % (str(bugid), local_file_name)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

    def socket_server_send(self, sock, data):
        try:
            sock.send(data)
        except Exception, e:
            print_string = "send data to socket client error %s" % e
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

        print_string = "recv data %s " % data
        print_info.print_info(print_info.PRINT_INFO, print_string)

        if len(self.socket_recv_data_remnant):
            data = self.socket_recv_data_remnant + data
            self.socket_recv_data_remnant = ''

        if '*' in data :
            cut_data = data.strip('*').split('*')
        else :
            if not data or data.decode('utf-8') == 'exit':
                sock.close()
                self.socket_client_list_lock.acquire()
                for x in self.socket_client_list:
                    if sock in x:
                        self.socket_client_list.pop(self.socket_client_list.index(x))
                        break
                self.socket_client_list_lock.release()

                self.dispense_work_list_lock.acquire()
                for i in range(len(dispense_work_list) - 1, -1, -1):
                    if sock in dispense_work_list[i] :
                        self.redispense_work_list.append(dispense_work_list[i])
                        dispense_work_list.pop(i)
                self.dispense_work_list_lock.release()
                return 0
            cut_data.append(data)

        print_string = "server socket recv data %s " % cut_data
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

        for recv_data_per in cut_data :
            if "username" in recv_data_per :
                if ':' in recv_data_per:
                    cut_data_per = recv_data_per.split(':')
                    self.socket_client_list_lock.acquire()
                    self.socket_client_list[self.socket_client_list.index([sock, addr])].append(cut_data_per[1])
                    self.socket_client_list_lock.release()
                    print_string = "client socket info(username) %s " % self.socket_client_list[self.socket_client_list.index([sock, addr, cut_data_per[1]])]
                    print_info.print_info(print_info.PRINT_INFO, print_string)
            elif "ftpspeed" in recv_data_per :
                if ':' in recv_data_per:
                    cut_data_per = recv_data_per.split(':')
                    self.socket_client_list_lock.acquire()
                    for x in self.socket_client_list:
                        if sock in x:
                            self.socket_client_list[self.socket_client_list.index(x)].append(int(cut_data_per[1]))
                            #test ----------------------------------------------------------------
                            a = [] + self.socket_client_list[0]
                            self.socket_client_list.append(a)
                            self.socket_client_list[1][3] = int(cut_data_per[1]) + 30
                            # test ----------------------------------------------------------------
                            self.socket_client_list.sort(reverse=True, key=lambda x: x[3])
                            print_string = "client socket info(speed) %s " % self.socket_client_list[self.socket_client_list.index(x)]
                            print_info.print_info(print_info.PRINT_INFO, print_string)
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
                    for x in bugid_max_index:
                        if download_ok_bugid in x:
                            if x[1] < download_ok_index:
                                self.bugid_max_index_lock.acquire()
                                self.bugid_max_index[bugid_max_index.index(x)][1] = download_ok_index
                                max_index = download_ok_index
                                self.bugid_max_index_lock.release()
                            else :
                                max_index = x[1]
                            break
                        else:
                            max_index_num += 1
                    if max_index_num == len(self.bugid_max_index) :
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
                for x in self.dispense_work_list :
                    if download_ok_bugid in x and download_ok_index in x :
                        dispense_work_list.pop(dispense_work_list.index(x))
                self.dispense_work_list_lock.release()

                for y in self.dispense_work_list:
                    if download_ok_bugid in y:
                        return 1

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
                print_string = "update code ok socket %s" % updatecodeok_socket
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
            elif len(recv_data_per) > 0:
                self.socket_recv_data_remnant = self.socket_recv_data_remnant + recv_data_per

        return 1

    def socket_server_status(self, sock, addr):
        print_string = 'Accept new connection from %s:%s...' % addr
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
        while True:
            recv_data = self.socket_server_recv(sock)
            if not self.handle_recv_data(sock, addr, recv_data):
                break
        print_string = "close connection from %s:%s..." % addr
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

    def socket_server_thread(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            self.socket_client_list.append([sock, addr])
            self.socket_server_send(sock, 'getusername*')
            self.socket_server_send(sock, 'getftpspeed*')
            self.socket_client_list_lock.release()
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