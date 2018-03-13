#!/usr/bin/python
# -*- coding:utf-8 -*-
import pexpect
import os 
import sys
import time
import print_info

ssh_ip = ''
ssh_port = 22
ssh_user = ''
ssh_password = ''
local_path = ''
remote_path = ''

class ssh_scp():
    def __init__(self, ip, port, user, password, localpath, remotepath):
        global ssh_ip
        global ssh_port
        global ssh_user
        global ssh_password
        global local_path
        global remote_path

        ssh_ip = ip
        ssh_port = port
        ssh_user = user
        ssh_password = password
        local_path = localpath
        remote_path = remotepath

#       print_string = "ip: %s; port: %d; user: %s ; password: %s" % (ip, port, user, password)
#       print_info.print_info(print_info.PRINT_DEBUG, print_string)
        print_string = "local path : %s \nremote path : %s" % (local_path, remote_path)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

    def ssh_exec_scp(self, dst_file, src_file):
        for x in range(3,13) :
            try :
                print_string = "scp file : %s to %s ... " % (src_file, dst_file)
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
                scp_command=pexpect.spawn('/usr/bin/scp -r ' + src_file + ' ' + dst_file, timeout = x*100)
                expect_result = scp_command.expect([r'assword:',r'yes/no'],timeout = 300)
                if expect_result == 0:
                    scp_command.sendline(ssh_password)
                    scp_command.read()
                elif expect_result == 1:
                    print_info.print_info(print_info.PRINT_DEBUG, 'ssh scp :send yes')
                    scp_command.sendline('yes')
                    scp_command.expect('assword:',timeout = 300)
                    scp_command.sendline(ssh_password)
                    scp_command.read()
            except Exception, e :
                print_string = "ssh scp file error %d:%s" % (x,e)
                print_info.print_info(print_info.PRINT_ERROR, print_string)
            else :
                print_string = "ssh scp file %s to %s ok" % (src_file, dst_file)
                print_info.print_info(print_info.PRINT_INFO, print_string)
                return 1
        return 0
    def scp_file_to_dst(self, local_file):
        ret = self.ssh_exec_scp(ssh_user + '@' + ssh_ip + ':' + remote_path, local_path + '/' + local_file)
        return ret

    def scp_file_dst_to_local(self, local_dir):
        ret = self.ssh_exec_scp(local_path, ssh_user + '@' + ssh_ip + ':' + remote_path + '/' + local_dir)
        return ret

if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
    ssh_scp_test = ssh_scp('10.0.70.102', 22, 'apuser', '123456', '/home/local/SPREADTRUM/lc.fan/flc/code/pybz/test', '/home/apuser/Web_Buglist')
    ssh_scp_test.scp_file_to_dst("pybz.zip")
    ssh_scp_test.scp_file_dst_to_local('apply-v4.0')