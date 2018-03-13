#!/usr/bin/python
#encoding=utf-8

import print_info

#max speed 100M 100,000,000
ftp_speed_max = 100000000

#work list:ftp, port, user, password, path, filename, size
#sock_list:sock, addr, client_user_name, speed
#dispense_work_list:sock, ftp, port, user, password, path, filename, start, size, index
def dispense_work(work, sock_list):
    client_speed_sum = 0
    speed_min = ftp_speed_max
    speed_max = 0
    sock_ftp_speed_list = []
    dispense_work_list = []
    ftp_download_index = 0
    ftp_file_size = 0
    ftp_file_start = 0
    dispense_size_per = 0
    client_download_size = 0

    try:
        ftp_file_size = int(work[6])
    except Exception, e:
        print_string = "dispense work file size error %s" % e
        print_info.print_info(print_info.PRINT_ERROR, print_string)
        return (0,"dispense work file size error")

    for x in sock_list:
        print_string = "sock addr:%s ftp downdload speed %d bit/s" % (x[1], x[3])
        print_info.print_info(print_info.PRINT_DEBUG, print_string)
        try:
            if x[3] >= 0 and x[3] < ftp_speed_max:
                client_speed_sum += x[3]
                if x[3] < speed_min:
                    speed_min = x[3]
                if x[3] > speed_max:
                    speed_max = x[3]
                sock_ftp_speed_list.append([x[0], x[1], x[2], x[3]])
        except Exception, e:
                print_string = "dispense work get speed error %s" % e
                print_info.print_info(print_info.PRINT_ERROR, print_string)
    if not client_speed_sum:
        return (0, 'client ftp speed is 0')
    dispense_size_per = int(ftp_file_size / client_speed_sum)

    for x in sock_ftp_speed_list:
        client_download_size = dispense_size_per * x[3]
        if (ftp_file_size - client_download_size - ftp_file_start) < (dispense_size_per * speed_min):
            client_download_size = ftp_file_size - ftp_file_start
        dispense_work_list.append([x[0], work[0], work[1], work[2], work[3], work[4],  work[5],
                                   ftp_file_start, client_download_size, ftp_download_index])
        ftp_file_start = ftp_file_start + client_download_size
        if ftp_file_start >= ftp_file_size:
            break
        ftp_download_index += 1

    return (1, dispense_work_list)

def redispense_work(dispense_work_client_list, sock_list):
    redispense_work_list = []
    sock_sum = len(sock_list)
    sock_index_num = 0

    for x in range(len(dispense_work_client_list)-1, -1, -1):
        dispense_work_client_list[x][0] = sock_list[sock_index_num % sock_sum][0]
        redispense_work_list.append(dispense_work_client_list[x])
        sock_index_num += 1
        dispense_work_client_list.pop(x)

    return redispense_work_list

def dispense_work_group(work_list, sock_list):
    group_dispense_work_list = []

    for x in work_list:
        dispense_list = dispense_work(x, sock_list)
        if dispense_list[0]:
            group_dispense_work_list.append(dispense_list[1])

    return group_dispense_work_list


if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
    group_work_list = []
    sock_list = []

    group_work_list.append(["ftp.spreadtrum.com", 21, "spreadst", r"spread$26?ST",
                            '/Testlogs/FAETest/Bugzilla_log/Bug 831329', '103.7z', 3561256])
    group_work_list.append(["ftp.spreadtrum.com", 21, "spreadst", r"spread$26?ST",
                            '/Testlogs/FAETest/Bugzilla_log/Bug 831329', '125.7z', 15682563])

    sock_list.append([1546, '10.0.70.40', 'lc.fan', 136])
    sock_list.append([1550, '10.0.70.41', 'lc.fan1', 764])
    sock_list.append([1551, '10.0.70.42', 'lc.fan2', 283])
    sock_list.append([1552, '10.0.70.43', 'lc.fan3', 349])

    sock_list.sort(reverse=True,key=lambda x:x[3])
    print_string = "sock list %s" % sock_list
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

    list = dispense_work_group(group_work_list, sock_list)
    for x in list:
        for y in x:
            print_string = "dispense work list %s" % y
            print_info.print_info(print_info.PRINT_DEBUG, print_string)