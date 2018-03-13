#!/usr/bin/python
#encoding=utf-8

import os
import sys
import time
import print_info
from ftplib import FTP
import threading



class download_ftp(FTP):
    ftp_download_speed = 100000
    ftp_download_speed_lock = threading.Lock()

    def __init__(self, ip, port, user, password):
        self.remoteip = ip
        self.remoteport = port
        self.user = user
        self.password = password

    def connect_ftp_server(self, fd):
        for n in range(3):
            try:
                # set 10s timeout
                fd.connect(self.remoteip, self.remoteport, 10)
            except Exception, e:
                print_string = "conncet ftp server failed - %s" % e
                print_info.print_info(print_info.PRINT_ERROR, print_string)
            else:
                try:
                    fd.login(self.user, self.password)
                except Exception, e:
                    print_string = 'login ftp server failed - %s' % e
                    print_info.print_info(print_info.PRINT_ERROR, print_string)
                else:
                    print_info.print_info(print_info.PRINT_DEBUG, 'login ftp server success')
                    return (1, 'connect ftp server success')
        print_info.print_info(print_info.PRINT_ERROR, 'connect ftp server failed')
        return (0, 'connect ftp server failed')

    def chang_work_dir(self, fd, remotefilepatch):
        #change remote work dir
        try:
            #fd.set_pasv(0)
            fd.cwd(remotefilepatch)
        except Exception, e:
            print_string = 'ftp change dir error %s' % e
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            return (0, 'ftp change dir error')
        else:
            print_string = 'change dir to: %s' % remotefilepatch
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
            print_string = "ftp dir is %s" % fd.pwd()
            print_info.print_info(print_info.PRINT_DEBUG, print_string)
            return (1, 'change dir OK')

    def get_ftp_filesize(self, fd, remotefilepatch, remotefilename, bugid):
        ftp_file_list = []
        fsize = 0
        change_ret = fd.chang_work_dir(fd, remotefilepatch)
        if change_ret[0]:
            try:
                dir_list = fd.nlst()
                print_string = 'dir file list %s' % dir_list
                print_info.print_info(print_info.PRINT_DEBUG, print_string)
            except Exception, e:
                print_string = 'get ftp dir error %s' % e
                print_info.print_info(print_info.PRINT_ERROR, print_string)
                return (0, 'get ftp dir error')

            for x in dir_list:
                if remotefilename:
                    if remotefilename == x:
                        try:
                            fsize = fd.size(remotefilename)
                        except Exception, e:
                            print_string = 'ftp get file %s size error %s' % (remotefilename, e)
                            print_info.print_info(print_info.PRINT_ERROR, print_string)
                            return (0, 'ftp get file size error')
                        else:
                            ftp_file_list.append([remotefilename, fsize])
                            print_string = 'get file name %s size %d' % (remotefilename, fsize)
                            print_info.print_info(print_info.PRINT_INFO, print_string)
                            return (1, ftp_file_list)
                elif str(bugid) in x:
                    try:
                        fsize = fd.size(x)
                    except Exception, e:
                        print_string = 'ftp get file %s size error %s' % (x, e)
                        print_info.print_info(print_info.PRINT_ERROR, print_string)
                        return (0, 'ftp get file size error')
                    else:
                        ftp_file_list.append([x, fsize])
                        print_string = 'get file name %s size %d' % (x, fsize)
                        print_info.print_info(print_info.PRINT_INFO, print_string)
            #ftp_file_list form [[file name, file size], [file name, file size]]
            return (1, ftp_file_list)

        else:
            return change_ret

    def download_ftp_file_size(self, fd, remotefilepatch, remotefilename, localfilepath, bugid, filename, start, size):
        lsize = 0
        cmpsize = 0
        time_start = time.time()

        if size == 0:
            return (1, "remote file size is null")

        if not os.path.exists(localfilepath + '/' + str(bugid)):
            os.mkdir(localfilepath + '/' + str(bugid))
            print_string = 'mkdir local file path %s' % (localfilepath + '/' + str(bugid))
            print_info.print_info(print_info.PRINT_DEBUG, print_string)

        localfilename = localfilepath + '/' + str(bugid) + '/' + filename
        if os.path.exists(localfilename):
            lsize = os.stat(localfilename).st_size
        if lsize >= size:
            print_string = 'file %s is exist, download file ok' % filename
            print_info.print_info(print_info.PRINT_INFO, print_string)
            return (1, print_string)

        change_ret = fd.chang_work_dir(fd, remotefilepatch)
        if not change_ret[0]:
            return change_ret

        blocksize = 1024 * 8
        cmpsize = lsize

        fd.voidcmd('TYPE I')
        try:
            download_file_conn = fd.transfercmd('RETR ' + remotefilename, start + lsize)
        except Exception, e:
            print_string = "ftp transfer cmd error %s" % e
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            return (0, 'time out-----ftp transfer cmd error')

        while True:
            if (size - cmpsize) < blocksize:
                blocksize = size - cmpsize
            try:
                data = download_file_conn.recv(blocksize)
            except Exception, e:
                print_string = 'receive data error %s' % e
                print_info.print_info(print_info.PRINT_ERROR, print_string)
                return (0, 'time out --ftp get file data error')
            if not data:
                break
            with open(localfilename, 'ab') as lwrite:
                lwrite.write(data)

            cmpsize += len(data)
            print '\r','download process:%.2f%%' % (float(cmpsize) / size * 100),
        print ''
        time_use = time.time() - time_start
        file_size = cmpsize - lsize
        self.ftp_download_speed_lock.acquire()
        self.ftp_download_speed = (int)(file_size / time_use)
        self.ftp_download_speed_lock.release()
        print_string = 'ftp download file %s ok .\ndownload size %d use time is %0.2f s; speed is %d bit/s' % \
                       (filename, file_size, time_use, self.ftp_download_speed)
        print_info.print_info(print_info.PRINT_INFO, print_string)

        try:
            download_file_conn.close()
            fd.voidcmd('NOOP')
            fd.voidresp()
        except Exception, e:
            print_string = 'close ftp conn error %s' % e
            print_info.print_info(print_info.PRINT_ERROR, print_string)

        if cmpsize >= size:
            print_string = 'download file %s ok' % filename
            print_info.print_info(print_info.PRINT_INFO, print_string)
            return (1, print_string)
        else:
            print_string = "local file size %d ,remote file size %d " % (cmpsize, size)
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            os.remove(localfilename)
            return (0, 'download file size error')

    def ftp_close(self, fd):
        try:
            fd.quit()
        except Exception, e:
            print_string = 'ftp:%s quit error %s ' % (fd, e)
            print_info.print_info(print_info.PRINT_ERROR, print_string)
        else:
            print_string = 'ftp:%s quit ok' % fd
            print_info.print_info(print_info.PRINT_DEBUG, print_string)


if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
    list = []
    i = 0
    ftp_fd = download_ftp("ftp.spreadtrum.com", 21, "spreadst", "spread$26?ST");
    ftp_fd.connect_ftp_server(ftp_fd)
    #file_list = ftp_fd.get_ftp_filesize(ftp_fd, '/TestLogs/India/SharkL2/MOCORDROID8.1_Trunk_18A_SHARKL2_W18.07.1/20180221', '103.7z', 834147)
    file_list = ftp_fd.get_ftp_filesize(ftp_fd, '/Testlogs/PSST/AndroidO/Pike2/MOCORDROID8.0_Trunk_PIKE2_W17.46.4', '786123.7z', 786123)
    if file_list[0]:
        list = file_list[1]
        while i < len(list):
            ftp_fd.download_ftp_file_size(ftp_fd, '/Testlogs/PSST/AndroidO/Pike2/MOCORDROID8.0_Trunk_PIKE2_W17.46.4', list[i][0],
                                         '/home/local/SPREADTRUM/lc.fan/flc/code/pybz', 786123, list[i][0], 0, list[i][1])
            i += 1;

    i = 0
    file_list = ftp_fd.get_ftp_filesize(ftp_fd, '/Testlogs/PSST/KaiOS/9820E/SPRDROID6.0_KAIOS_17D_W18.03.2', '', 821366)
    if file_list[0]:
        list = file_list[1]
        print_string = 'remote file list %s' % list
        print_info.print_info(print_info.PRINT_INFO, print_string)
        while i < len(list):
            ftp_fd.download_ftp_file_size(ftp_fd, '/Testlogs/PSST/KaiOS/9820E/SPRDROID6.0_KAIOS_17D_W18.03.2',
                                          list[i][0], '/home/local/SPREADTRUM/lc.fan/flc/code/pybz', 821366,
                                          list[i][0], 0, list[i][1])
            i += 1;
    ftp_fd.ftp_close(ftp_fd)
