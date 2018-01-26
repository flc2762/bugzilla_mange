# -*- coding:utf-8 -*-
#import paramiko
import pexpect
import os 
import sys
import time

ssh_ip = '10.0.70.41'
ssh_port = 22
ssh_user = 'apuser'
ssh_password = '123456'

def ssh_scp_put(ip,port,user,password,local_file,remote_file):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(_ip, port, user, password)
	err = ssh.exec_command('date')
	stdin, stdout, stderr = err
	print stdout.read()
	sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
	sftp = ssh.open_sftp()
	sftp.put(local_file, remote_file)

def ssh_scp_get(ip, port, user, password, remote_file, local_file):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, port, user, password)
	err = ssh.exec_command('date')
	stdin, stdout, stderr = err
	print stdout.read()
	sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
	sftp = ssh.open_sftp()
	sftp.get(remote_file, local_file)

def ssh_exec_scp(local_file, remote_file):
	for x in range(10) :
		try :
#			cmd_temp = 'scp -r ' + local_file +' apuser@' + ssh_ip + ':' + remote_file
#			print "cmd : %s" % cmd_temp
			scp_command=pexpect.spawn('scp -r ' + local_file +' apuser@' + ssh_ip + ':' + remote_file)
			expect_result = scp_command.expect([r'assword:',r'yes/no'],timeout=60)
			if expect_result == 0:
				print "scp file : %s to apuser@%s:%s... " % (local_file, ssh_ip, remote_file)
				scp_command.sendline(ssh_password)
				scp_command.read()
			elif expect_result == 1:
				print "scp file : %s to apuser@%s:%s... " % (local_file, ssh_ip, remote_file)
				scp_command.sendline('yes')
				scp_command.expect('assword:',timeout=60)
				scp_command.sendline(ssh_password)
				scp_command.read()
		except Exception, e :
			print "ssh scp file error %d:%s" % (x, e)
		else : 
			print "scp file ok"
			return 1
	return 0

if __name__ == '__main__':
	local_file = '/home/local/SPREADTRUM/lc.fan/flc/code/pybz/748921/123.rar'
	remote_file = '/home/apuser/bug_work/buglist/748921/123.rar'
	print 'test ssh'
	ssh_exec_scp(local_file, remote_file)
#	ssh_scp_put(ssh_ip, ssh_port, ssh_user, ssh_password, local_file, remote_file)
	
