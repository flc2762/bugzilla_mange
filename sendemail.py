#!/usr/bin/python

import sys
import datetime
import print_info
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

src_addr = ''
src_password = ''
src_smtp = ''

class send_email():

    def __init__(self, addr, password, smtp):
        global src_addr
        global src_password
        global src_smtp

        src_addr = addr
        src_password = password
        src_smtp = smtp
#       print_string = "source address is %s; source password: %s" % (src_addr, src_password)
#       print_info.print_info(print_info.PRINT_DEBUG, print_string)

    def send_email(self, msg_head, msg_info, dest_addr):
        msg = MIMEMultipart('alternative')
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg['Subject'] = "%s ---- %s " % (msg_head, time_now)
        msg['From'] = src_addr
        msg['To'] = dest_addr
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"
        html = '<html><body><p>%s</p></body></html>' % msg_info
        part2 = MIMEText(html, 'html',sys.getfilesystemencoding())

        msg.attach(part2)

        s = smtplib.SMTP_SSL(src_smtp)
        s.login(src_addr, src_password)

        s.sendmail(src_addr, dest_addr, msg.as_string())
        s.quit()

    def send_email_group(self, msg_head, msg_info, dest_addr_list):
        s = smtplib.SMTP_SSL(src_smtp)
        s.login(src_addr, src_password)
        html = '<html><body><p>%s</p></body></html>' % msg_info
        part2 = MIMEText(html, 'html',sys.getfilesystemencoding())
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "%s ---- %s " % (msg_head,time_now)
        msg['From'] = src_addr
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"


        for addr in dest_addr_list:
            msg['To'] = addr
            msg.attach(part2)
            s.sendmail(src_addr, addr, msg.as_string())

        s.quit()

if __name__ == '__main__':
    print_info.init(print_info.PRINT_DEBUG)
    mail_addr_group = []

    send_email = send_email("fanlc@spreadst.com", r"fanlc123456789",
			                "mail.spreadst.com")
    send_email.send_email("test head", "test info", "fanlc@spreadst.com")
    mail_addr_group.append("fanlc@spreadst.com")
    mail_addr_group.append("fanlc@spreadst.com")
    print 'addr group %s' % mail_addr_group
#    send_email.send_email_group("test head", "test info to group", mail_addr_group)