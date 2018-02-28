#!/usr/bin/python

import print_info

def save_write(path,file_name,contents):
	save_file = path + '/' + file_name
	f = open(save_file,'w+')
	f.write(contents)
	f.close()
def read_data(path,file_name):
	read_file = path + '/' + file_name
	f = open(read_file,'r')
	data = f.read()
	f.close()
	return data

def save_append(path,file_name,contents):
	save_file = path + '/' + file_name
	f = open(save_file,'ab')
	f.write(contents)
	f.close()

def read_line(path,file_name):
	read_file = path + '/' + file_name
	f = open(read_file,'r')
	lines = f.readlines()
	f.close()
	return lines

if __name__ == '__main__':
	print_info.init(print_info.PRINT_INFO)
	save_write("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file", "log_status:0\n")
	data = read_data("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file")
	print_info.print_info(print_info.PRINT_INFO, data)
	save_append("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file", "symbols_status:0:3\n")
	data_list = read_line("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file")
	for x in data_list :
		print_info.print_info(print_info.PRINT_INFO, x)
		if ':' in x:
			cut_data = x.split(':')
			if 'log_status' in cut_data[0]:
				if int(cut_data[1]) == 0:
					break
	data_list[data_list.index(x)] = 'log_status:1:2'
	s = '\n'.join(data_list)
	save_write("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file", s)
	data = read_data("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file")
	print_info.print_info(print_info.PRINT_INFO, data)