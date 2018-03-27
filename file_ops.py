#!/usr/bin/python

import print_info


def save_write(path, file_name, contents):
    save_file = path + '/' + file_name
    f = open(save_file, 'wb')
    f.write(contents)
    f.close()


def read_data(path, file_name):
    read_file = path + '/' + file_name
    f = open(read_file, 'rb')
    data = f.read()
    f.close()
    return data


def save_append(path, file_name, contents):
    save_file = path + '/' + file_name
    f = open(save_file, 'ab')
    f.write(contents)
    f.close()


def read_line(path, file_name):
    read_file = path + '/' + file_name
    f = open(read_file, 'rb')
    lines = f.readlines()
    f.close()
    return lines


if __name__ == '__main__':
    print_info.init(print_info.PRINT_INFO)
    save_write("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file", "log_status:0" + '\n')
    file_data = read_data("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file")
    print_info.print_info(print_info.PRINT_INFO, file_data)
    save_append("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file", "symbols_status:0:3" + '\n')
    data_list = read_line("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file")
    for x in data_list:
        if '\n' in x:
            # delete '\n'
            data_list[data_list.index(x)] = x.strip('\n')

    for x in data_list:
        print 'data line % s ' % x
        print_info.print_info(print_info.PRINT_INFO, x)
        if ':' in x:
            cut_data = x.split(':')
            if 'symbols_status' in cut_data[0]:
                if int(cut_data[1]) == 0:
                    break
    data_list[data_list.index(x)] = 'symbols_status:1:2'
    s = '\n'.join(data_list) + '\n'
    save_write("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file", s)
    data_list = read_line("/home/local/SPREADTRUM/lc.fan/flc/code/pybz", "test_file")
    print_info.print_info(print_info.PRINT_INFO, data_list)