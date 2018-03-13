#!/usr/bin/python

import os
import sys
import sched
import time
import datetime
import ConfigParser
import threading
import socket
import fcntl
import struct
import file_ops
import print_info
import dispense_work
import ftpdownloadfile
#import httpdownloadfile
#import ftpdownloadfile
#import socket_server
#import socket_client
#import dispense_work
#from rest import API
#from sambadownloadfile import download_samba
#from sendemail import send_email


#main path save download file directory, log and so on
MAIN_PATH = ''
LOG_DIR = 'log'
KERNEL_FILE_NAME_BASE = '.kernel_python_log'
save_log_file_lock = threading.Lock()

#time
TIME_NOW = ''
TIME_NOW_DATE = ''
TIME_NUM = 0

#schedule task per time
SCHEDULE_TASK = ''

#config version
CONFIG_VERSION = 0.01
CONFIG_PRINT_LEVEL = 1

#bugzilla conig
BUGZILLA_USERNAME = ''
BUGZILLA_PASSWORD = ''
KERNEL_MEMBERS = []
STATUS_FIELDS = []
PRODUCT_FIELDS = []
DEFAULT_FIELDS = []

#mail config
MAIL_ADDR = ''
MAIL_PASSWORD = ''
MAIL_SMTP = ''
SEND_MAIL_ADDRESS = []

#ftp server info, ip, user, password
FTP_SERVER_INFO = []
FTP_SERVER_PORT = 21

#samba server info
SAMBA_USERNAME = ''
SAMBA_PASSWORD = ''
SAMBA_REMOTEIP = ''

#socket info
SOCKET_SERVER_IP = ''
SOCKET_SERVER_PORT = 1234
SOCKET_SIZE = 1024
SOCKET_CONNECT = 50
SOCKET_MODE = 0
SOCKET_AUTO_MODE = 0
SOCKET_SERVER_MODE = 1
SOCKER_CLIENT_MODE = 2

SCP_SERVER_IP = ''
SCP_USER= ''
SCP_PASSWORD = ''
SCP_DIR = ''

UPDATE_CODE = 0

CODE_PATH = ''

SEARCH_BUG_PARAM = {'product': 'Sprdroid_7.0_iWhale2','status': 'Assigned', 'assigned_to': 'fanlc@spreadst.com'}

DOWNLOAD_LOG_FTP = 0
DOWNLOAD_SYMBOLS_SAMBA = 1
DOWNLOAD_SYMBOLS_HTTP = 2

DOWNLOAD_START = 4
DOWNLOAD_OK = 3
DOWNLOAD_FAIL = 0

DOWNLOAD_STATUS_FILE_NAME = '.downloadfilestatus'
file_status_lock = threading.Lock()
DOENLOAD_END_FILE_NAME = 'bug_id_statistics'
file_download_end_lock = threading.Lock()

current_bug_all = []
kernel_group_buglist_old = []
kernel_group_buglist_man = []
kernel_group_buglist_new = []
socket_fd = 0

ftp_get_bug_log_fail = []
local_download_bug_log_list =[]
local_download_bug_log_list_lock = threading.Lock()

def read_item(config_par, item):
    string_temp = ''
    try:
        string_temp = config_par.get('info', item)
    except Exception, e:
        print_string = "get item error %s" % e
        print_info.print_info(print_info.PRINT_ERROR, print_string)
        return (0, "get item error")
    else:
        if len(string_temp):
            return (1,string_temp)
        else:
            print_string = "get item is null"
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
            return (0, "get item is null")

def read_config():

    global CONFIG_VERSION
    global CONFIG_PRINT_LEVEL
    global print_info_fd
    global BUGZILLA_USERNAME
    global BUGZILLA_PASSWORD
    global KERNEL_MEMBERS
    global STATUS_FIELDS
    global PRODUCT_FIELDS
    global DEFAULT_FIELDS

    global FTP_SERVER_INFO
    global SAMBA_USERNAME
    global SAMBA_PASSWORD
    global SAMBA_REMOTEIP

    global MAIL_ADDR
    global MAIL_PASSWORD
    global MAIL_SMTP
    global SEND_MAIL_ADDRESS

    global SOCKET_SERVER_IP
    global SOCKET_SERVER_PORT
    global SOCKET_MODE

    global SCP_SERVER_IP
    global SCP_USER
    global SCP_PASSWORD
    global SCP_DIR

    global UPDATE_CODE

    get_item_ret = []
    cut_config_temp = []

    config_parser = ConfigParser.ConfigParser()
    with open('./config', 'rw') as configfd:
        config_parser.readfp(configfd)

    get_item_ret = read_item(config_parser, 'CONFIG_VERSION')
    if get_item_ret[0]:
        if CONFIG_VERSION == float('%.2f' % float(get_item_ret[1])):
            return
        CONFIG_VERSION = float('%.2f' % float(get_item_ret[1]))
        print_string = 'config cersion: V%.2f ' % CONFIG_VERSION
        print_info.print_info(print_info.PRINT_INFO, print_string)
    else:
        print_string = "get config version error"
        print_info.print_info(print_info.PRINT_ERROR, print_string)
        return

    get_item_ret = read_item(config_parser, 'CONFIG_PRINT_LEVEL')
    if get_item_ret[0]:
        CONFIG_PRINT_LEVEL = int(get_item_ret[1])
        print_string = 'CONFIG_PRINT_LEVEL = %d ' % CONFIG_PRINT_LEVEL
        print_info.print_info(print_info.PRINT_INFO, print_string)
        if CONFIG_PRINT_LEVEL != print_info.PRINT_LEVEL:
            print_info.init(CONFIG_PRINT_LEVEL)

    get_item_ret = read_item(config_parser, 'BUGZILLA_USERNAME')
    if get_item_ret[0]:
        BUGZILLA_USERNAME = get_item_ret[1]
        print_string = 'BUGZILLA_USERNAME = %s ' % BUGZILLA_USERNAME
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'BUGZILLA_PASSWORD')
    if get_item_ret[0]:
        BUGZILLA_PASSWORD = get_item_ret[1]
        print_string = 'BUGZILLA_PASSWORD = %s ' % BUGZILLA_PASSWORD
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'KERNEL_MEMBERS')
    if get_item_ret[0]:
        KERNEL_MEMBERS = get_item_ret[1].split(',')
        print_string = 'KERNEL_MEMBERS = %s ' % KERNEL_MEMBERS
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'STATUS_FIELDS')
    if get_item_ret[0]:
        STATUS_FIELDS = get_item_ret[1].split(',')
        print_string = 'STATUS_FIELDS =  %s ' % STATUS_FIELDS
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'PRODUCT_FIELDS')
    if get_item_ret[0]:
        PRODUCT_FIELDS = get_item_ret[1].split(',')
        print_string = 'PRODUCT_FIELDS =  %s ' % PRODUCT_FIELDS
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'DEFAULT_FIELDS')
    if get_item_ret[0]:
        DEFAULT_FIELDS = get_item_ret[1].split(',')
        print_string = 'DEFAULT_FIELDS =  %s ' % DEFAULT_FIELDS
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'FTP_SERVER_INFO')
    if get_item_ret[0]:
        cut_config_temp = get_item_ret[1].split(';')
        for x in cut_config_temp:
            FTP_SERVER_INFO.append([x.split(',')[0], x.split(',')[1], x.split(',')[2]])
        print_string = 'FTP_SERVER_INFO = %s ' % FTP_SERVER_INFO
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SAMBA_USERNAME')
    if get_item_ret[0]:
        SAMBA_USERNAME = get_item_ret[1]
        print_string = 'SAMBA_USERNAME = %s ' % SAMBA_USERNAME
        print_info.print_info(print_info.PRINT_INFO, print_string)
    get_item_ret = read_item(config_parser, 'SAMBA_PASSWORD')
    if get_item_ret[0]:
        SAMBA_PASSWORD = get_item_ret[1]
        print_string = 'SAMBA_PASSWORD = %s ' % SAMBA_PASSWORD
        print_info.print_info(print_info.PRINT_INFO, print_string)
    get_item_ret = read_item(config_parser, 'SAMBA_REMOTEIP')
    if get_item_ret[0]:
        SAMBA_REMOTEIP = get_item_ret[1]
        print_string = 'SAMBA_REMOTEIP = %s ' % SAMBA_REMOTEIP
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'MAIL_ADDR')
    if get_item_ret[0]:
        MAIL_ADDR = get_item_ret[1]
        print_string = 'MAIL_ADDR = %s ' % MAIL_ADDR
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'MAIL_PASSWORD')
    if get_item_ret[0]:
        MAIL_PASSWORD = get_item_ret[1]
        print_string = 'MAIL_PASSWORD = %s ' % MAIL_PASSWORD
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'MAIL_SMTP')
    if get_item_ret[0]:
        MAIL_SMTP = get_item_ret[1]
        print_string = 'MAIL_SMTP = %s ' % MAIL_SMTP
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SEND_MAIL')
    if get_item_ret[0]:
        SEND_MAIL_ADDRESS = get_item_ret[1].split(',')
        print_string = 'SEND_MAIL_ADDRESS =  %s ' % SEND_MAIL_ADDRESS
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SOCKET_SERVER_IP')
    if get_item_ret[0]:
        SOCKET_SERVER_IP = get_item_ret[1]
        print_string = 'SOCKET_SERVER_IP = %s ' % SOCKET_SERVER_IP
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SOCKET_SERVER_PORT')
    if get_item_ret[0]:
        SOCKET_SERVER_PORT = int(get_item_ret[1])
        print_string = 'SOCKET_SERVER_PORT = %d ' % SOCKET_SERVER_PORT
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SOCKET_MODE')
    if get_item_ret[0]:
        SOCKET_MODE = int(get_item_ret[1])
        print_string = 'SOCKET_MODE = %d ' % SOCKET_MODE
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SCP_SERVER_IP')
    if get_item_ret[0]:
        SCP_SERVER_IP = get_item_ret[1]
        print_string = 'SCP_SERVER_IP = %s ' % SCP_SERVER_IP
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SCP_USER')
    if get_item_ret[0]:
        SCP_USER = get_item_ret[1]
        print_string = 'SCP_USER = %s ' % SCP_USER
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SCP_PASSWORD')
    if get_item_ret[0]:
        SCP_PASSWORD = get_item_ret[1]
        print_string = 'SCP_PASSWORD = %s ' % SCP_PASSWORD
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'SCP_DIR')
    if get_item_ret[0]:
        SCP_DIR = get_item_ret[1]
        print_string = 'SCP_DIR = %s ' % SCP_DIR
        print_info.print_info(print_info.PRINT_INFO, print_string)

    get_item_ret = read_item(config_parser, 'UPDATE_CODE')
    if get_item_ret[0]:
        UPDATE_CODE = int(get_item_ret[1])
        print_string = 'UPDATE_CODE = %d ' % UPDATE_CODE
        print_info.print_info(print_info.PRINT_INFO, print_string)

def save_log_info_to_file(str):
    save_log_file_lock.acquire()
    file_ops.save_append(MAIN_PATH + '/' + LOG_DIR, KERNEL_FILE_NAME_BASE + TIME_NOW_DATE, str)
    save_log_file_lock.release()

def list_members_bugs_single(api, product, member, status):
    bug_info_list = []

    params = SEARCH_BUG_PARAM
    params.update({"status":status})
    params.update({"assigned_to":member})
    params.update({"product":product})
    for b in api.bug_get(params):
        bug_info = {}
        for f in DEFAULT_FIELDS:
            if f in b:
                bug_info[f] = str(b[f])
        bug_info_list.append(bug_info)
    return bug_info_list

def get_kernel_bug_all(api):
    bugs_info_all = []
    for p in  PRODUCT_FIELDS:
        print_string = "get %s bug..." % p
        print_info.print_info(print_info.PRINT_INFO, print_string)
        save_log_info_to_file(print_string + '\n')
        for m in  KERNEL_MEMBERS:
            for s in STATUS_FIELDS:
                list_a_bug = list_members_bugs_single(api,p,m,s)
                if len(list_a_bug):
                    for x in list_a_bug:
                        bugs_info_all.append(x)
    return bugs_info_all

def make_kernel_bug_contents(bugs_all):
    temp_table_init = []
    bugs_table_contents = {}
    bugs_sum_table = []
    index = 0

    temp_table_init = [0] * (len(KERNEL_MEMBERS) + 1)

    for x in KERNEL_MEMBERS:
        bugs_table_contents[x] = [] + temp_table_init
    bugs_table_contents['Total'] = [] + temp_table_init

    for bug_dict in bugs_all:
        for key in bug_dict.keys():
            if key == 'product':
                if bug_dict[key] in PRODUCT_FIELDS:
                    index = PRODUCT_FIELDS.index(bug_dict[key])
                else:
                    continue

            if key == 'assigned_to':
                if bug_dict[key] in KERNEL_MEMBERS:
                    bugs_table_contents[bug_dict[key]][index] += 1
                    bugs_table_contents['Total'][index] += 1
                    index = 0

    bugs_sum_table.append(bugs_table_contents)
    return bugs_sum_table

def get_bug_id_list(bugs_all):
    bugs_id_list = []
    for bug_dict in bugs_all:
        for key in bug_dict.keys():
            if key == 'id':
                bugs_id_list.append(bug_dict[key])
    return bugs_id_list

def save_bugs_table(bug_sum):
    table_title = {'Kernel_bugs':PRODUCT_FIELDS}
    file_contents = ''

    for key, value in table_title.items():
        file_contents = file_contents + '|' + '%30s' % key
        for i in range(len(PRODUCT_FIELDS)):
            file_contents = file_contents + '|' + '%25s' % value[i]
        file_contents += '\n'

    for key, value in bug_sum[0].items():
        if key != 'Total':
            file_contents = file_contents + '|' + '%30s' % key
            for i in range(len(PRODUCT_FIELDS)):
                file_contents = file_contents + '|' + '%25s' % value[i]
            file_contents += '\n'
    # add Total to file_contents end
    file_contents = file_contents + '|' + '%30s' % 'Total'
    for i in range(len(PRODUCT_FIELDS)):
        file_contents = file_contents + '|' + '%25s' % bug_sum[0]['Total'][i]
    file_contents += '\n'

    return file_contents

def get_bugs_info_str(bug_all):
    bugs_info_str = []
    bugs_info_str.append('    ')
    s = ''
    for bug_dict in bug_all:
        for x in DEFAULT_FIELDS:
            if x in bug_dict.keys():
                bugs_info_str.append(str(bug_dict[x]))
        bugs_info_str.append('\n')

    s = "    ".join(bugs_info_str)
    return s

def save_bugs_info_file(bug_sum, bug_all, bug_list):
    f_time_line = TIME_NOW + '\n'
    file_contents = f_time_line + 'Current bugs:\n'
    file_contents += save_bugs_table(bug_sum)
    file_contents += "\n\nKernel group all bugs (Total %s):\nbugid: " % len(bug_list) + ', '.join(bug_list) + '\n'
    file_contents += get_bugs_info_str(bug_all)
    file_ops.save_write(MAIN_PATH, 'kernel_bug_info', file_contents)

    print_string = "save to file bug info: \n%s" % file_contents
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

def email_html_table(bug_sum):
    file_contents = ''
    table_title_temp = {'Kernel_bugs': PRODUCT_FIELDS}
    table_title = '<font color="#FF0000"> Kernel Group bugs statistics:</font> \n'
    tds = []
    sum_temp = 0

    for name, value in bug_sum[0].items():
        if name != 'Total':
            tds.append('<tr><td>%s</td>' % name)
            for i in range(len(PRODUCT_FIELDS)):
                tds.append('<td>%s</td>' % value[i])
                sum_temp += value[i]
            tds.append('<td>%s</td></tr>' % sum_temp)
            sum_temp = 0

    tds.append('<tr><td>%s</td>' % 'Total')
    for i in range(len(PRODUCT_FIELDS)):
        tds.append('<td>%s</td>' % bug_sum[0]['Total'][i])
        sum_temp += bug_sum[0]['Total'][i]
    tds.append('<td>%s</td></tr>' % sum_temp)
    sum_temp = 0
    file_contents = file_contents + '<table border="1">'
    file_contents = file_contents + '<caption>'
    file_contents = file_contents + u'%s' % table_title.replace('\n', '<br>')
    file_contents = file_contents + '</caption>'
    file_contents = file_contents + '<tr><th>%s</th>' % table_title_temp.keys()[0]
    for i in range(len(PRODUCT_FIELDS)):
        file_contents = file_contents + '<th>%s</th>' % table_title_temp['Kernel_bugs'][i]
    file_contents = file_contents + '<td>Total</td></tr>'
    file_contents = file_contents + ''.join(tds)
    file_contents = file_contents + '</table>'
    return file_contents

def email_html_table_bug_detail(bug_all):
    table_tile = '<font color="#FF0000"> Kernel Group bugs Detail: </font> \n'
    file_contents = ''
    tds = []

    for bug_dict in bug_all:
        tds.append('<tr>')
        for f in DEFAULT_FIELDS:
            if f in bug_dict.keys():
                if bug_dict['id'] in kernel_group_buglist_new:
                    tds.append('<td><font color="#FF0000">%s</font></td>' % bug_dict[f])
                else:
                    tds.append('<td>%s</td>' % bug_dict[f])
    tds.append('</tr>')
    file_contents += '<table border="1">'
    file_contents += '<caption>'
    file_contents += u'%s' % table_tile.replace('\n', '<br>')
    file_contents += '</caption>'
    file_contents += '<tr>'
    for x in DEFAULT_FIELDS:
        file_contents += '<th>%s</th>' % x
    file_contents = file_contents + '</tr>'
    file_contents = file_contents + ''.join(tds)
    file_contents = file_contents + '</table>'

    return file_contents

def send_bugs_info_mail(current_bug_sum, current_bug_all, current_bug_list):
    from sendemail import send_email
    send_email_info = email_html_table(current_bug_sum)
    str_info= "\n\nKernel group all bugs (Total %s):\n" % len(current_bug_list) + ', '.join(current_bug_list) + '\n'
    str_info += "kernel group handle bug: %s \nkernel group increase bug: %s \n\n" % \
                (len(kernel_group_buglist_old) + len(kernel_group_buglist_new) - len(current_bug_list),
                 len(kernel_group_buglist_new))
    send_email_info += str_info.replace('\n', '<br>')
    send_email_info += email_html_table_bug_detail(current_bug_all)

    send_email_api = send_email(MAIL_ADDR, MAIL_PASSWORD, MAIL_SMTP)
    send_email_api.send_email('Kernel Group bugs statistics', send_email_info, 'fanlc@spreadst.com')

def send_bugs_download_ok_mail(bug_ok_list):
    from sendemail import send_email
    send_email_info = ''

    send_email_info += "\ndownload bug log ok: \n" + str(bug_ok_list) +'\n\n'
    send_email_info +="get bug log from:'%s@%s:%s/bugid' password:%s\nor\nget bug log from:'smb://10.0.70.102/bug_image' login:%s passwor:%s" % \
                      (SCP_USER, SCP_SERVER_IP, SCP_DIR, SCP_PASSWORD, SCP_USER, SCP_PASSWORD)
    send_email_info = send_email_info.replace('\n','<br>')

    send_email_api = send_email(MAIL_ADDR, MAIL_PASSWORD, MAIL_SMTP)
    send_email_api.send_email_group('Kernel Group bugs download log ok', send_email_info, SEND_MAIL_ADDRESS)

def handle_samba_params(path, name):
    #handle name
    file_name = ''
    file_name_back = ''
    file_name_cut = []
    symbols_dir = ''
    path_cut = []
    samba_dir = ''
    samba_path = ''

    if 'sp' in name:
        file_name = name[name.index('sp'):]
        file_name_cut = file_name.split('_')
        # get symbols file name and symbols dir
        for x in file_name_cut:
            if '-' in x:
                file_name = symbols_dir
                symbols_dir = symbols_dir + x
                #symbols file name:
                #symbols.vmlinux.sp9832e_1h10_oversea-userdebug-native.tgz
                #symbols.vmlinux.sp7731e_14c20_native_userdebug_native.tgz
                file_name_back = 'symbols.vmlinux.' + file_name + x.replace('-', '_') + '.tgz'
                file_name = 'symbols.vmlinux.' + file_name + x + '.tgz'
                break
            symbols_dir = symbols_dir + x + '_'

    #handle path
    if '10.0.1.110\\' in path:
        path = path[path.index('10.0.1.110\\') + len('10.0.1.110\\'):].strip()
        path_cut = path.split('\\')
        samba_dir = path_cut[0]
        samba_path = path[path.index(path_cut[1]):]
    if '\Images' not in samba_path:
        samba_path = samba_path + '\Images'
    else:
        samba_path = samba_path[:samba_path.index('\Images') + len('\Images')]

    samba_path = samba_path.replace('\\', '/') + '/' + symbols_dir

    return (samba_path, samba_dir, file_name, file_name_back)

def download_file_isok(bugid, file_flag_string):
    cut_data = []
    if os.path.exists(MAIN_PATH + '/' + str(bugid) + '/' + DOWNLOAD_STATUS_FILE_NAME):
        download_file_status = file_ops.read_line(MAIN_PATH + '/' + str(bugid), DOWNLOAD_STATUS_FILE_NAME)
        for x in download_file_status:
            if ':' in x:
                cut_data = x.split(':')
                if file_flag_string in cut_data[0]:
                    break
            cut_data = []
        if len(cut_data) > 1:
            if int(cut_data[1]) == DOWNLOAD_OK:
                return 1

    return 0

def save_download_status_file(bugid, file_flag_string, status, server):
    cut_data = []
    s = ''
    file_status_lock.acquire()
    if os.path.exists(MAIN_PATH + '/' + str(bugid) + '/' + DOWNLOAD_STATUS_FILE_NAME):
        download_file_status = file_ops.read_line(MAIN_PATH + '/' + str(bugid), DOWNLOAD_STATUS_FILE_NAME)
        print_string = 'read bugid %s:%s' % (str(bugid), download_file_status)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
        for x in download_file_status:
            if '\n' in x:
                #delete '\n'
                download_file_status[download_file_status.index(x)] = x.strip('\n')
        for x in download_file_status:
            if ':' in x:
                cut_data = x.split(':')
                if file_flag_string in cut_data[0]:
                    break
            cut_data = []
        if len(cut_data):
            download_file_status[download_file_status.index(x)] = file_flag_string + ':' + str(status) + ':' + str(server)
            s = '\n'.join(download_file_status) + '\n'
            file_ops.save_write(MAIN_PATH + '/' + str(bugid), DOWNLOAD_STATUS_FILE_NAME, s)
        else:
            s = file_flag_string + ':' + str(status) + ':' + str(server) + '\n'
            file_ops.save_append(MAIN_PATH + '/' + str(bugid), DOWNLOAD_STATUS_FILE_NAME, s)
    else:
        s = file_flag_string + ':' + str(status) + ':' + str(server) + '\n'
        file_ops.save_append(MAIN_PATH + '/' + str(bugid), DOWNLOAD_STATUS_FILE_NAME, s)
    file_status_lock.release()

def save_download_end_file(bugid, status_info):
    file_download_end_lock.acquire()
    file_ops.save_append(MAIN_PATH, DOENLOAD_END_FILE_NAME, 'download bug id log ' + str(bugid) + status_info)
    file_download_end_lock.release()

def download_symbols_from_samba(path, name, bugid):
    from sambadownloadfile import download_samba
    ret = 0
    samba_path_dir_name = []
    if download_file_isok(bugid, 'symbols_status'):
        print_string = 'download bugid %s symbols file is exist from samba' % str(bugid)
        print_info.print_info(print_info.PRINT_INFO, print_string)
        return

    samba_path_dir_name = handle_samba_params(path, name)
    print_string = 'samba path:%s \nsamba dir:%s \nfile name:%s' % \
                   (samba_path_dir_name[0], samba_path_dir_name[1], samba_path_dir_name[2])
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

    save_download_status_file(bugid, 'symbols_status', DOWNLOAD_START, DOWNLOAD_SYMBOLS_SAMBA)

    smb_fd = download_samba(SAMBA_REMOTEIP, samba_path_dir_name[1], SAMBA_USERNAME, SAMBA_PASSWORD)

    ret = smb_fd.download_samba_file(samba_path_dir_name[0], MAIN_PATH + '/' + str(bugid), samba_path_dir_name[2])

    if ret:
        save_download_status_file(bugid, 'symbols_status', DOWNLOAD_OK, DOWNLOAD_SYMBOLS_SAMBA)
        print_string = 'download bugid %s symbols from samba ok' % str(bugid)
        print_info.print_info(print_info.PRINT_INFO, print_string)
    else:
        ret = smb_fd.download_samba_file(samba_path_dir_name[0], MAIN_PATH + '/' + str(bugid), samba_path_dir_name[3])
        if ret:
            save_download_status_file(bugid, 'symbols_status', DOWNLOAD_OK, DOWNLOAD_SYMBOLS_SAMBA)
            print_string = 'download bugid %s symbols from samba ok' % str(bugid)
            print_info.print_info(print_info.PRINT_INFO, print_string)
        else:
            save_download_status_file(bugid, 'symbols_status', DOWNLOAD_FAIL, DOWNLOAD_SYMBOLS_SAMBA)
            print_string = 'download bugid %s symbols from samba fail' % str(bugid)
            print_info.print_info(print_info.PRINT_ERROR, print_string)

def handle_http_params(path, name):
    file_name = ''
    file_name_back = ''
    file_name_cut = []
    file_name_list = []
    symbols_dir = ''
    path_cut = []
    http_path = ''
    http_path_back = ''
    http_path_list = []

    if '_' in name:
        if 'sp' in name:
            file_name = name[name.index('sp'):]
        file_name_cut = file_name.split('_')
        # get symbols file name and symbols dir
        for x in file_name_cut:
            if '-' in x:
                file_name = symbols_dir
                symbols_dir = symbols_dir + x
                # symbols file name:
                # symbols.vmlinux.sp9832e_1h10_oversea-userdebug-native.tgz
                # symbols.vmlinux.sp7731e_14c20_native_userdebug_native.tgz
                file_name_back = 'symbols.vmlinux.' + file_name + x.replace('-', '_') + '.tgz'
                file_name = 'symbols.vmlinux.' + file_name + x + '.tgz'
                file_name_list.append(file_name)
                file_name_list.append(file_name_back)
                break
            symbols_dir = symbols_dir + x + '_'

        if 'http' in path:
            path = path[path.index('http'):]
        #delete '/'
        path = path.strip('/')
        if 'daily_build' in path:
            path_cut = path.split('/')
            for x in path_cut:
                if 'daily_build' in x:
                    http_path = path + '/artifact/' + x
        else:
            http_path = path + '/artifact'
        http_path_back = http_path + '/SYMBOLS/' + symbols_dir
        http_path += '/Images/' + symbols_dir
        http_path_list.append(http_path)
        http_path_list.append(http_path_back)

        return (1 , http_path_list, file_name_list)
    else:
        return (0,path)

def download_symbols_from_jenkins(path, name, bugid):
    import httpdownloadfile
    ret = []
    http_path_dir_name = []
    if download_file_isok(bugid, 'symbols_status'):
        print_string = 'download bugid %s symbols file is exist from http ' % str(bugid)
        print_info.print_info(print_info.PRINT_INFO, print_string)
        return

    http_path_dir_name = handle_http_params(path, name)
    if http_path_dir_name[0]:
        save_download_status_file(bugid, 'symbols_status', DOWNLOAD_START, DOWNLOAD_SYMBOLS_HTTP)
        for x in http_path_dir_name[1]:
            for y in http_path_dir_name[2]:
                ret = httpdownloadfile.download_http(x, MAIN_PATH + '/' + str(bugid), y)
                if ret[0]:
                    break
                print_string = 'http path:%s \nhttp name: %s' % (x, y)
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
            if ret[0]:
                break
        if ret[0]:
            save_download_status_file(bugid, 'symbols_status', DOWNLOAD_OK, DOWNLOAD_SYMBOLS_HTTP)
            print_string = 'download bugid %s symbols from http ok' % str(bugid)
            print_info.print_info(print_info.PRINT_INFO, print_string)
        else:
            save_download_status_file(bugid, 'symbols_status', DOWNLOAD_FAIL, DOWNLOAD_SYMBOLS_HTTP)
            print_string = 'download bugid %s symbols from http server fail' % str(bugid)
            print_info.print_info(print_info.PRINT_ERROR, print_string)
    else:
        save_download_status_file(bugid, 'symbols_status', DOWNLOAD_FAIL, DOWNLOAD_SYMBOLS_HTTP)
        print_string = 'download bugid %s symbols from http fail' % str(bugid)
        print_info.print_info(print_info.PRINT_ERROR, print_string)

def handle_ftp_params(server, path, name):
    path_lower = ''
    path_cut = []
    ftp_path = ''
    ftp_file_name = ''
    ftp_server_num = 0
    ftp_server = r'ftp.spreadtrum.com'

    ftp_path = path
    ftp_file_name = name
    if len(path):
        if r'(' in path:
            # delete bug 740894 zhongwenzifu 741537
            ftp_path = path[:path.index(r'(')]
        elif u'\uff08' in path:
            # delete bug 741537 zhongwenzifu
            ftp_path = path[:path.index(u'\uff08')]

        path_lower = ftp_path.lower()
        if 'bugid' in path_lower:
            if '/' in path:
                path_cut = path.split('/')
            else:
                path_cut = path.split('\\')

            ftp_path = ''
            for x in path_cut:
                if 'bugid' in x.lower():
                    break
                ftp_path += x + '/'
        else:
            if len(name):
                ftp_file_name = name
            else:
                if '.gz' in path or '.rar' in path or '.7z' in path or '.zip' in path:
                    ftp_file_name = path[path.rfind('\\') + 1:]
                    ftp_path = path[:path.rfind('\\')]
        if len(server) > 0:
            ftp_server = r'ftp.spreadtrum.com'
        else:
            if 'ftp.spreadtrum.com/' in path:
                ftp_server = r'ftp.spreadtrum.com'
            if 'ftp.spreadtrum.com/' in ftp_path:
                ftp_path = ftp_path[ftp_path.index('ftp.spreadtrum.com/') + len('ftp.spreadtrum.com/'):]
        ftp_server_num = 0
    else:
        if 'ftp.spreadtrum.com/' in server:
            ftp_path = server[server.index('ftp.spreadtrum.com/') + len('ftp.spreadtrum.com/'):]
            ftp_server = r'ftp.spreadtrum.com'
        if 'ftp.spreadtrum.com\\' in server:
            ftp_path = server[server.index('ftp.spreadtrum.com\\') + len('ftp.spreadtrum.com\\'):]
            ftp_server = r'ftp.spreadtrum.com'
        if 'bugid' in ftp_path.lower():
            if '/' in ftp_path:
                path_cut = ftp_path.split('/')
            else:
                path_cut = ftp_path.split('\\')
            ftp_path = ''
            for x in path_cut:
                if 'bugid' in x.lower():
                    break
                ftp_path += x + '/'
            # sharklE
            if r'/sharkle/' in ftp_path:
                ftp_path = ftp_path.replace(r'/sharkle/', r'/sharklE/')
        ftp_server_num = 1

    ftp_path = ftp_path.replace('\\', '/').strip('/').strip()

    return (ftp_server, ftp_path, ftp_file_name, ftp_server_num)

#data form:[0:<socket_fd, 1:ftp server, 2:ftp port, 3:ftp user, 4:ftp password, 5:ftp download file path,
#               6:file name, 7:start size, 8:download size, 9:index, 10:bugid]
#[<socket._socketobject object at 0x7f3a9fbbd750>, 'ftp.spreadtrum.com', 21, 'spreadst', 'spread$26?ST',
# u'Testlogs/PSST/Android8.1/PIKE2/MOCORDROID8.1_Trunk_PIKE2_W18.06.2', '103.7z', 0, 2012790, 0, 123456]
def send_download_work_to_client(data):

    send_data = 'downloadlog:bugid:' + str(data[10]) + ';ftpserver:'+ data[1] + ';ftpport:'+ str(data[2]) + \
                ';ftpuser:'+ data[3] + ';ftppw:'+ data[4] + ';filepath:'+ data[5] + ';filename:'+ data[6] + \
                ';start:'+ str(data[7]) + ';size:'+ str(data[8]) + ';index:'+ str(data[9]) + '*'

    if socket_fd.socket_server_send(data[0], send_data):
        socket_fd.dispense_work_list_lock.acquire()
        socket_fd.dispense_work_list.append(data)
        socket_fd.dispense_work_list_lock.release()
        return 1
    else:
        socket_fd.dispense_work_list_lock.acquire()
        socket_fd.redispense_work_list.append(data)
        socket_fd.dispense_work_list_lock.release()
        return 0

def local_download_bug_log(params):
    #local ftp download file
    ret = []
    local_ftp_fd = ftpdownloadfile.download_ftp(params[0], params[1], params[2], params[3])

    for i in range(10):
        ret = local_ftp_fd.connect_ftp_server(local_ftp_fd)
        if ret[0]:
            ret = local_ftp_fd.download_ftp_file_size(local_ftp_fd, params[4], params[5], MAIN_PATH, params[7],
                                                      params[5], 0, params[6])
            if ret[0]:
                save_download_status_file(params[7], 'log_status', DOWNLOAD_OK, DOWNLOAD_LOG_FTP)
                save_download_end_file(params[7], ' end\n')
                for x in local_download_bug_log_list:
                    if params[7] in x:
                        local_download_bug_log_list_lock.acquire()
                        local_download_bug_log_list.pop(local_download_bug_log_list.index(x))
                        local_download_bug_log_list_lock.release()
                        break
                local_ftp_fd.ftp_close(local_ftp_fd)
                break
            local_ftp_fd.ftp_close(local_ftp_fd)
        print_string = 'download bugid %s log file again %d' % (str(params[7]), i)
        print_info.print_info(print_info.PRINT_INFO, print_string)

def download_log_from_ftp(server, path, name, bugid):
    ret = []
    ftp_path_dir_name = []
    ftp_fd = 0
    ftp_file_list = []
    not_dispense_work_list = []
    global local_download_bug_log_list
    fail_list_num = 0

    if download_file_isok(bugid, 'log_status'):
        print_string = 'download bugid %s log file is exist' % str(bugid)
        print_info.print_info(print_info.PRINT_INFO, print_string)
        return

    ftp_path_dir_name = handle_ftp_params(server, path, name)
    print_string = 'ftp server:%s ;  num:%d \nftp path:%s \nfile name:%s' % \
                   (ftp_path_dir_name[0], ftp_path_dir_name[3], ftp_path_dir_name[1], ftp_path_dir_name[2])
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

    # ftp download file
    ftp_fd = ftpdownloadfile.download_ftp(ftp_path_dir_name[0], 21,
                                          FTP_SERVER_INFO[ftp_path_dir_name[3]][1],
                                          FTP_SERVER_INFO[ftp_path_dir_name[3]][2])

    ret = ftp_fd.connect_ftp_server(ftp_fd)
    if ret[0]:
        ret = ftp_fd.get_ftp_filesize(ftp_fd, ftp_path_dir_name[1], ftp_path_dir_name[2], bugid)
        if len(kernel_group_buglist_new):
                save_download_end_file(bugid, ' start\n')
        if ret[0] and len(ret[1]):
            ftp_file_list = ret[1]
            print_string = 'download ftp file list %s' % ftp_file_list
            print_info.print_info(print_info.PRINT_DEBUG, print_string)

            if len(socket_fd.socket_client_list):
                for x in ftp_file_list:
                    not_dispense_work_list.append([ftp_path_dir_name[0], 21, FTP_SERVER_INFO[ftp_path_dir_name[3]][1],
                                          FTP_SERVER_INFO[ftp_path_dir_name[3]][2], ftp_path_dir_name[1], x[0], x[1]])
                dispense_finish_list = dispense_work.dispense_work_group(not_dispense_work_list, socket_fd.socket_client_list)

                for x in dispense_finish_list:
                    for y in x:
                        y.append(bugid)
                        print_string = 'dispense work: %s' % y
                        print_info.print_info(print_info.PRINT_DEBUG, print_string)
                        send_download_work_to_client(y)

            else:
                # add work to local download log list
                for x in ftp_file_list:
                    local_download_bug_log_list_lock.acquire()
                    local_download_bug_log_list.append([ftp_path_dir_name[0], 21,
                                                       FTP_SERVER_INFO[ftp_path_dir_name[3]][1],
                                                       FTP_SERVER_INFO[ftp_path_dir_name[3]][2],
                                                       ftp_path_dir_name[1], x[0], x[1], bugid])
                    print_string = 'add bug log info: filename %s size %d to local download' % (x[0], x[1])
                    print_info.print_info(print_info.PRINT_DEBUG, print_string)
                    local_download_bug_log_list_lock.release()

            if len(ftp_get_bug_log_fail):
                for i in range(len(ftp_get_bug_log_fail) - 1, -1, -1):
                    if bugid in ftp_get_bug_log_fail[i]:
                        ftp_get_bug_log_fail.pop(i)
                        break
        else:
            if len(ftp_get_bug_log_fail):
                for i in range(len(ftp_get_bug_log_fail) - 1, -1, -1):
                    if bugid in ftp_get_bug_log_fail[i]:
                        if ftp_get_bug_log_fail[i][1] > 5:
                            ftp_get_bug_log_fail.pop(i)
                            if fail_list_num > 0:
                                fail_list_num -= 1
                            kernel_group_buglist_old.append(bugid)
                            save_download_end_file(bugid, ' error\n')
                        else:
                            ftp_get_bug_log_fail[i][1] += 1
                        break
                    fail_list_num += 1
                if len(ftp_get_bug_log_fail) and fail_list_num == len(ftp_get_bug_log_fail):
                    ftp_get_bug_log_fail.append([bugid, 0])
                    print_string = 'fail_list_num :%d; add bugid %s to ftp_get_bug_log_fail' % (fail_list_num, str(bugid))
                    print_info.print_info(print_info.PRINT_DEBUG, print_string)
            else:
                ftp_get_bug_log_fail.append([bugid, 0])

def get_bug_file_path(api, bugid):
    log_path = ''
    log_file_name = ''
    log_ftp_server = ''
    symbols_name = ''
    version_path_samba = ''
    version_path_jenkins = ''
    symbols_name_http = ''
    downloadsymbolsthread = 0
    params = {'id': bugid}

    bug_data = api.bug_get_all_info(params)
#    print_string = 'bug id %s:\n %s' % (bugid, bug_data)
#    print_info.print_info(print_info.PRINT_DEBUG, print_string)
    if 'bugs' in bug_data:
        first_comment = bug_data['bugs'][str(bugid)][bug_data.keys()[1]][0]
        first_comment_text = first_comment[first_comment.keys()[3]].split('\n')
#       print_string = 'bug id %s first comment:\n %s' % (bugid, first_comment_text)
#       print_info.print_info(print_info.PRINT_DEBUG, print_string)
    else:
        return

    for x in first_comment_text:
        if r'\TestLogs' in x:
            if not len(log_path):
                log_path = x[x.index(r'\TestLogs'):]
        elif r'\Testlogs' in x:
            if not len(log_path):
                log_path = x[x.index(r'\Testlogs'):]
        elif r'.rar' in x or r'.zip' in x or r'.7z' in x:
            log_file_name = x
        elif 'ftp.spreadtrum.com' in x:
            if not len(log_ftp_server):
                log_ftp_server = x
        # get vmlinux samba server
        elif 'Project' in x:
            if not len(symbols_name):
                symbols_name = x
        elif '10.0.1.110' in x:
            if not len(version_path_samba):
                if ':' in x:
                    version_path_samba = x.split(':')[1]
                else:
                    version_path_samba = x
        # get vmlinux jenkins server
        elif 'jenkins' in x:
            version_path_jenkins = x
        elif 'Pac:' in x:
            if not len(symbols_name_http):
                symbols_name_http = x

    print_string = 'bug id %s log path: %s' % (bugid, log_path)
    print_info.print_info(print_info.PRINT_DEBUG, print_string)
    if len(log_file_name):
        print_string = 'bug id %s log file name: %s' % (bugid, log_file_name)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
    print_string = 'bug id %s log ftp server: %s' % (bugid, log_ftp_server)
    print_info.print_info(print_info.PRINT_DEBUG, print_string)
    if len(symbols_name):
        print_string = 'bug id %s symbols name: %s' % (bugid, symbols_name)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
    if len(version_path_samba):
        print_string = 'bug id %s samba path: %s' % (bugid, version_path_samba)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
    if len(version_path_jenkins):
        print_string = 'bug id %s jenkins path: %s' % (bugid, version_path_jenkins)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
    if len(symbols_name_http):
        print_string = 'bug id %s jenkins name: %s' % (bugid, symbols_name_http)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

    if len(version_path_samba):
        downloadsymbolsthread = threading.Thread(target=download_symbols_from_samba,
                                                 args=(version_path_samba, symbols_name, bugid),
                                                 name='sambadownloadsymbols')
        downloadsymbolsthread.setDaemon(True)
        downloadsymbolsthread.start()
    elif len(version_path_jenkins):
        if not len(symbols_name_http):
            symbols_name_http = symbols_name
        downloadsymbolsthread = threading.Thread(target=download_symbols_from_jenkins,
                                                 args=(version_path_jenkins, symbols_name_http, bugid),
                                                 name='httpdownloadsymbols')
        downloadsymbolsthread.setDaemon(True)
        downloadsymbolsthread.start()

    download_log_from_ftp(log_ftp_server, log_path, log_file_name, bugid)


def download_log_files(api, bug_id_list):
    for x in bug_id_list:
        if not os.path.exists(MAIN_PATH + '/' + str(x)):
            os.mkdir(MAIN_PATH + '/' + str(x))
            print_string = 'mkdir bug id dir %s' % (MAIN_PATH + '/' + str(x))
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
        else:
            if download_file_isok(x, 'log_status') and download_file_isok(x, 'symbols_status'):
                continue
        print_string = "download bug id %s log ..." % x
        print_info.print_info(print_info.PRINT_INFO, print_string)
        save_log_info_to_file(print_string + '\n')
        if len(current_bug_all):
            for bugid_info in current_bug_all:
                if x == bugid_info['id']:
                    if not os.path.exists(MAIN_PATH + '/' + str(x) + '/' + '.bugid_info'):
                        file_ops.save_write(MAIN_PATH + '/' + str(x), '.bugid_info', (bugid_info['product']))
        get_bug_file_path(api, x)

def manipulating_download_bug_log():
    global kernel_group_buglist_new
    global kernel_group_buglist_man
    manipulating_bugid_info = []

    if os.path.exists(MAIN_PATH + "/manu_buglist"):
        manipulating_download_buglist = file_ops.read_line(MAIN_PATH, "manu_buglist")
        if len(manipulating_download_buglist):
            file_ops.save_write(MAIN_PATH, "manu_buglist", "")
            print_string = "get manu info %s " % str(manipulating_download_buglist)
            print_info.print_info(print_info.PRINT_INFO, print_string)
            save_log_info_to_file(print_string + '\n')
            for x in manipulating_download_buglist:
                if ',' in x:
                    if '\n' in x:
                        x = x.replace("\n", "")
                    manipulating_bugid_info = x.split(',')
                    if '\\' in manipulating_bugid_info[1]:
                        ftp_file_name = manipulating_bugid_info[1][manipulating_bugid_info[1].rfind('\\') + 1:]
                        ftp_path = manipulating_bugid_info[1][:manipulating_bugid_info[1].rfind('\\')]
                    else:
                        ftp_file_name = manipulating_bugid_info[1][manipulating_bugid_info[1].rfind('/') + 1:]
                        ftp_path = manipulating_bugid_info[1][:manipulating_bugid_info[1].rfind('/')]
                    kernel_group_buglist_new.append(manipulating_bugid_info[0])
                    kernel_group_buglist_man.append(manipulating_bugid_info[0])
                    if not os.path.exists(MAIN_PATH + '/' + str(manipulating_bugid_info[0])):
                        os.mkdir(MAIN_PATH + '/' + str(manipulating_bugid_info[0]))
                        print_string = 'manu mkdir bug id dir %s' % (MAIN_PATH + '/' + str(manipulating_bugid_info[0]))
                        print_info.print_info(print_info.PRINT_DEBUG, print_string)
                    else:
                        if download_file_isok(manipulating_bugid_info[0], 'log_status'):
                            continue
                    # ftp server
                    if 'testlogs' in ftp_path.lower():
                        download_log_from_ftp('', ftp_path, ftp_file_name, manipulating_bugid_info[0])
                    else:
                        download_log_from_ftp(ftp_path, '', ftp_file_name, manipulating_bugid_info[0])
                    manipulating_bugid_info = []
            kernel_group_buglist_new = []

def update_code_socket_client():
    if UPDATE_CODE:
        if len(socket_fd.socket_client_list):
            for x in socket_fd.socket_client_list:
                if x[1][0] not in socket_fd.update_code_addr_list:
                    socket_fd.socket_server_send(x[0], 'updatecode*')
                    socket_fd.update_code_addr_list_lock.acquire()
                    socket_fd.update_code_addr_list.append(x[1][0])
                    socket_fd.update_code_addr_list_lock.release()
                    print_string = 'main:send updatecode to sock:%s' % x[1][0]
                    print_info.print_info(print_info.PRINT_DEBUG, print_string)
    else:
        socket_fd.update_code_addr_list_lock.acquire()
        socket_fd.update_code_addr_list = []
        socket_fd.update_code_addr_list_lock.release()

def snapshot():
    from rest import API
    global kernel_group_buglist_old
    global kernel_group_buglist_man
    global kernel_group_buglist_new
    global current_bug_all
    ftp_get_bug_log_fail_num = 0
    get_bug_log_fail_list = []
    dispense_work_to_local_list = []

    #read config file
    read_config()

    #update socket clinet code
    update_code_socket_client()

    print_string = "now time: %s " % TIME_NOW
    print_info.print_info(print_info.PRINT_INFO, print_string)
    save_log_info_to_file(print_string + '\n')

    bugzilla_api = API('http://bugzilla.spreadtrum.com/bugzilla', 'False', 'None', 'None')
    ret = bugzilla_api.login(BUGZILLA_USERNAME, BUGZILLA_PASSWORD)
    if not ret:
        print_string = "snapshot: %s Login ok !" % BUGZILLA_USERNAME
        print_info.print_info(print_info.PRINT_INFO, print_string)
        save_log_info_to_file(print_string + '\n')
    else:
        print_string = "snapshot: %s Login error !" % BUGZILLA_USERNAME
        print_info.print_info(print_info.PRINT_ERROR, print_string)

    for x in socket_fd.socket_client_list:
        print_string = "socket client:%s" % x
        print_info.print_info(print_info.PRINT_INFO, print_string)
        save_log_info_to_file(print_string + '\n')

    #save donwload log status
    socket_fd.download_log_ok_list_lock.acquire()
    if len(socket_fd.download_log_ok_list):
        for x in socket_fd.download_log_ok_list:
            save_download_status_file(x, 'log_status', DOWNLOAD_OK, DOWNLOAD_LOG_FTP)
            save_download_end_file(x, ' end\n')
        send_bugs_download_ok_mail(socket_fd.download_log_ok_list)

        socket_fd.download_log_ok_list = []
    socket_fd.download_log_ok_list_lock.release()

    #read file ,manipulating download bug log
    manipulating_download_bug_log()
    print_string = "manu bug list: %s" % kernel_group_buglist_man
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

    current_bug_all = get_kernel_bug_all(bugzilla_api)
    print_string = "all bug info: %s" % current_bug_all
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

    current_bug_sum = make_kernel_bug_contents(current_bug_all)
    current_bug_list = get_bug_id_list(current_bug_all)

    for x in current_bug_list:
        if x not in kernel_group_buglist_old and x not in kernel_group_buglist_man:
            kernel_group_buglist_new.append(x)
    kernel_group_buglist_man = []

    print_string = "current bug list: %s" % current_bug_list
    print_info.print_info(print_info.PRINT_DEBUG, print_string)
    print_string = "old bug list: %s" % kernel_group_buglist_old
    print_info.print_info(print_info.PRINT_DEBUG, print_string)
    print_string = "new bug list: %s" % kernel_group_buglist_new
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

    save_bugs_info_file(current_bug_sum, current_bug_all, current_bug_list)

#test download log code-----------------------------------
#    kernel_group_buglist_new = []
#    kernel_group_buglist_new.append('837812')
#    kernel_group_buglist_new.append('841156')
#    kernel_group_buglist_new.append('832375')
#test download log code----------------------------------

    if len(kernel_group_buglist_new):
        send_bugs_info_mail(current_bug_sum, current_bug_all, current_bug_list)
        download_log_files(bugzilla_api, kernel_group_buglist_new)

    kernel_group_buglist_old = []
    for x in current_bug_list:
        kernel_group_buglist_old.append(x)
    kernel_group_buglist_new = []

    if len(socket_fd.socket_client_list):
        if len(socket_fd.redispense_work_list):
            print_string = "redispense work list:%s" % socket_fd.redispense_work_list
            print_info.print_info(print_info.PRINT_INFO, print_string)
            save_log_info_to_file(print_string + '\n')
            socket_fd.dispense_work_list_lock.acquire()
            socket_fd.socket_client_list_lock.acquire()
            redispense_work_new_list = dispense_work.redispense_work(socket_fd.redispense_work_list, socket_fd.socket_client_list)
            socket_fd.socket_client_list_lock.release()
            socket_fd.dispense_work_list_lock.release()
            for x in redispense_work_new_list:
                send_download_work_to_client(x)
    else:
        ftp_get_bug_log_fail_num = 0
        if len(socket_fd.dispense_work_list):
            for x in socket_fd.dispense_work_list:
                for y in dispense_work_to_local_list:
                    if x[-1] in y:
                        break
                    else:
                        ftp_get_bug_log_fail_num += 1
                if len(dispense_work_to_local_list) == ftp_get_bug_log_fail_num:
                    dispense_work_to_local_list.append([x[1], x[5], x[6], x[-1]])
                ftp_get_bug_log_fail_num = 0

        ftp_get_bug_log_fail_num = 0
        if len(socket_fd.redispense_work_list):
            for x in socket_fd.redispense_work_list:
                for y in dispense_work_to_local_list:
                    if x[-1] in y:
                        break
                    else:
                        ftp_get_bug_log_fail_num += 1
                if len(dispense_work_to_local_list) == ftp_get_bug_log_fail_num:
                    dispense_work_to_local_list.append([x[1], x[5], x[6], x[-1]])
                ftp_get_bug_log_fail_num = 0
        socket_fd.dispense_work_list_lock.acquire()
        socket_fd.dispense_work_list = []
        socket_fd.redispense_work_list = []
        socket_fd.dispense_work_list_lock.release()

    if len(dispense_work_to_local_list):
        for x in range(len(dispense_work_to_local_list) - 1, -1, -1):
            if 'testlogs' in dispense_work_to_local_list[x][1].lower():
                download_log_from_ftp('', dispense_work_to_local_list[x][0] + '/' + dispense_work_to_local_list[x][1],
                                      dispense_work_to_local_list[x][2], dispense_work_to_local_list[x][3])
            else:
                download_log_from_ftp(dispense_work_to_local_list[x][0] + '/' + dispense_work_to_local_list[x][1], '',
                                      dispense_work_to_local_list[x][2], dispense_work_to_local_list[x][3])
            dispense_work_to_local_list.pop(x)

    if len(local_download_bug_log_list):
        for x in local_download_bug_log_list:
            local_download_bug_log(x)

    if len(ftp_get_bug_log_fail):
        print_string = "ftp get log fail list: %s" % ftp_get_bug_log_fail
        print_info.print_info(print_info.PRINT_INFO, print_string)
        save_log_info_to_file(print_string + '\n')
        for x in ftp_get_bug_log_fail:
            get_bug_log_fail_list.append(x[0])
        download_log_files(bugzilla_api, get_bug_log_fail_list)

#test--------------------------
#    socket_fd.download_log_ok_list.append('833218')
#    socket_fd.download_log_ok_list.append('832375')
#test--------------------------

    socket_fd.download_log_ok_list_lock.acquire()
    if len(socket_fd.download_log_ok_list):
        for x in socket_fd.download_log_ok_list:
            save_download_status_file(x, 'log_status', DOWNLOAD_OK, DOWNLOAD_LOG_FTP)
            save_download_end_file(x, ' end\n')
        send_bugs_download_ok_mail(socket_fd.download_log_ok_list)

        socket_fd.download_log_ok_list = []
    socket_fd.download_log_ok_list_lock.release()

    current_bug_all = []
    print_string = "-------------------end------------------"
    print_info.print_info(print_info.PRINT_INFO, print_string)


def do_task(cmd):
    # we do this work time range 8~21 per 5 minute, exculde saturday and sunday
    global TIME_NUM
    global TIME_NOW
    global TIME_NOW_DATE

    try:

        TIME_NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        TIME_NOW_DATE = TIME_NOW.split(' ')[0]
        time_h = int(TIME_NOW.split(' ')[1].split(':')[0])
        day_of_week = datetime.datetime.now().weekday()

        print_string = 'time now is %s ;date is %s ' % (TIME_NOW, TIME_NOW_DATE)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)

        if day_of_week < 5:
            if (time_h > 7) & (time_h < 22):
                snapshot()
            else:
                if TIME_NUM > 12:
                    TIME_NUM = 0
                    snapshot()
                else:
                    TIME_NUM += 1
        else:
            if TIME_NUM > 12:
                TIME_NUM = 0
                snapshot()
            else:
                TIME_NUM += 1

    except Exception, e:
        print_string = 'error: run error: %s' % e
        print_info.print_info(print_info.PRINT_ERROR, print_string)
        #save except log to .kernel_python_logd+data
        save_log_info_to_file(print_string + '\n')


def run_cmd(cmd, count):
    do_task(cmd)
    SCHEDULE_TASK.enter(count, 0, run_cmd, (cmd, count))

def run_per_time(count):
    cmd = ''
    run_cmd(cmd, count)
    SCHEDULE_TASK.run()

def periodicity():
    global socket_fd

    if SOCKET_MODE == SOCKET_SERVER_MODE:
        import socket_server
        socket_fd = socket_server.socket_server(SOCKET_SERVER_IP, SOCKET_SERVER_PORT, SOCKET_SIZE, SOCKET_CONNECT)
        socket_fd.server_main_path = MAIN_PATH
        socket_fd.update_code = UPDATE_CODE
        print_string = "run python --------- server"
        print_info.print_info(print_info.PRINT_INFO, print_string)
        save_log_info_to_file(print_string + '\n')
        #wait socket clinet connect
        time.sleep(30)
        run_per_time(300)

    else:
        import socket_client
        socket_fd = socket_client.socket_client(SOCKET_SERVER_IP, SOCKET_SERVER_PORT, SOCKET_SIZE)
        socket_fd.client_main_path = MAIN_PATH
        socket_fd.scp_server_ip = SCP_SERVER_IP
        socket_fd.scp_user = SCP_USER
        socket_fd.scp_password = SCP_PASSWORD
        socket_fd.scp_dir = SCP_DIR
        socket_fd.code_path = CODE_PATH
        print_string = "run python --------- client "
        print_info.print_info(print_info.PRINT_INFO, print_string)
        save_log_info_to_file(print_string + '\n')


if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)

    CODE_PATH = sys.argv[0]
    MAIN_PATH = os.path.split(os.path.split(sys.argv[0])[0])[0]
    TIME_NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    TIME_NOW_DATE = TIME_NOW.split(' ')[0]

    if not os.path.exists(MAIN_PATH + '/' + LOG_DIR):
        os.mkdir(MAIN_PATH + '/' + LOG_DIR)
        print_string = 'mkdir log dir %s' % (MAIN_PATH + '/' + LOG_DIR)
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
    print_string = "main save path %s " % MAIN_PATH
    print_info.print_info(print_info.PRINT_DEBUG, print_string)
    save_log_info_to_file(print_string + '\n')
    read_config()
    if SOCKET_MODE == SOCKET_AUTO_MODE:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ifname = 'eth0'
            local_ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
            s.close()
            print_string = "local is:%s" % local_ip
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
            if local_ip == SOCKET_SERVER_IP:
                SOCKET_MODE = SOCKET_SERVER_MODE
            else:
                SOCKET_MODE = SOCKER_CLIENT_MODE
        except Exception, e:
            print_string = 'get local ip:%s' % e
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            SOCKET_MODE = SOCKER_CLIENT_MODE

    SCHEDULE_TASK = sched.scheduler(time.time, time.sleep)
    periodicity()
