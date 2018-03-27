#!/usr/bin/python
import os
import time
import requests
import print_info

def download_http(html_path, localfilepath, filename):
    urlrequest = 0
    fd = 0

    time_start = time.time()

    print_string = 'get file %s ...' % filename
    print_info.print_info(print_info.PRINT_INFO,  print_string)

    try:
        urlrequest = requests.get(html_path + '/' + filename, timeout=30)
    except:
        return (0, 'time out')

    if int(urlrequest.status_code) > 400:
        print_string = 'get file error %d ' % int(urlrequest.status_code)
        print_info.print_info(print_info.PRINT_WARNING, print_string)
        return (0, 'get file error')

    print_string = 'get file status %d ' % int(urlrequest.status_code)
    print_info.print_info(print_info.PRINT_DEBUG, print_string)

    with open(localfilepath + r'/' + filename, "wb") as fd:
        fd.write(urlrequest.content)

    time_use = time.time() - time_start
    file_size = os.path.getsize(localfilepath + r'/' + filename)
    http_download_speed = (int)(file_size / time_use)
    print_string = 'http download file %s end .\ndownload size %d use time is %0.2f s; speed is %d bit/s' % \
                   (filename, file_size, time_use, http_download_speed)
    print_info.print_info(print_info.PRINT_INFO, print_string)

    if urlrequest.headers.get('content-length', 0):
        if os.path.getsize(localfilepath + r'/' + filename) >= int(urlrequest.headers['content-length']):
            print_info.print_info(print_info.PRINT_INFO, 'get file size ok')
            return (1, 'get file size ok')
        else:
            print_string = 'local size %d  html size %d ' % (os.path.getsize(localfilepath + r'/' + filename),
                                                             int(urlrequest.headers['content-length']))
            print_info.print_info(print_info.PRINT_ERROR, print_string)
            return (0, 'get file size error')
    print_string = 'get symbols %s ok' % filename
    print_info.print_info(print_info.PRINT_INFO, print_string)
    return (1, 'get symbols ok')

if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
    download_http('http://download.jetbrains.com/python',
            '/home/local/SPREADTRUM/lc.fan/flc/code/pybz',
            'pycharm-professional-2017.3.2.tar.gz')
    download_http('http://10.29.1.90:8080/jenkins/job/6.0_kaios_17d_temp/413/artifact/Images/sp9820e_1h10_k_4m_native-userdebug-native',
                  '/home/local/SPREADTRUM/lc.fan/flc/code/pybz',
#                  'sp9820e_1h10_k_4m_native-userdebug-native.tar.gz')
                  'sp9820e_1h10_k_4m_native-userdebug-native.build.log')
