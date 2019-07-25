#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 这个脚本是在服务器上添加新用户并自动发送邮件通知

import smtplib
from email.header import Header
from email.mime.text import MIMEText

__author__ = "yang.cong"
__version__ = "1.0"

import os
import logging


logging.basicConfig(filename='test.log', level=logging.INFO, format='[%(asctime)s] %(filename)s[line:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def get_up():
    """
    you will get a list with username, userpasswand and useremail
    :return: list
    """
    name_id = input("请输入要新增的员工号: ")
    name_mail = input("请输入要发送的邮箱(默认163.com,不使用此邮箱请完整输入): ")
    list_mail = list(name_mail)
    if "@" in list_mail:
        name_mail = name_mail
    else:
        name_mail = name_mail + "@163.com"

    # 由于Linux用户不能以数字开头，可以自定义
    new_user = "test" + name_id
    user_pwd = "Test" + name_id
    return [new_user, user_pwd, name_mail]


def open_passwd(obj):
    """
    open the passwd file to check if exist user
    :return:
    """
    passwd_file = open("/etc/passwd", mode='r', encoding="utf-8")
    user_list = []
    for line in passwd_file.readlines():
        user_list.append(line.split(":")[0])
    if obj[0] in user_list:
        logging.error("已存在%s此用户, 程序退出" % obj[0])
        exit(99)
    else:
        logging.info("准备添加新用户%s" % obj[0])
        add_user(obj)


def add_user(obj):
    """
    add user
    :return:
    """
    res_adduser = os.system('useradd  %(name1)s -M -s /sbin/nologin' % {'name1': obj[0]})
    if res_adduser == 0:
        logging.info("添加用户%s成功" % obj[0])
        res_changepwd = os.system('echo %(pass)s | passwd --stdin %(name1)s' % {'name1': obj[0], 'pass': obj[1]})
        if res_changepwd == 0:
            logging.info("修改%(n)s用户密码成功为%(pwd)s" % {'n': obj[0], 'pwd': obj[1]})
            send_mail2(obj)
        else:
            logging.error("修改用户密码失败, 请检查")
            exit(99)
    else:
        logging.error("添加用户失败, 请检查")
        exit(99)


def send_mail1():
    """
    this is a function of send mail with use Shell
    :return:
    """
    try:
        if os.path.exists("sendEmail"):
            get_cmd = "./sendEmail -f " + FROMMAIL + " -t " + DBAEMAIL + " -s " + SMTPHOST + " -u " + Title + " -xu " + FROMMAIL + " -xp " + SMTPASS + " -m 你的密码是%s" % user_pwd
            res = os.system(get_cmd)
            if res == 0:
                logging.info("发送邮件成功")
            else:
                logging.error("发送邮件失败")
        else:
            os.system("wget -c --no-check-certificate http://dl.itopm.com/tools/sendEmail")
            md5sm = os.popen("md5sum sendEmail").read().split()[0]
            if md5sm == "1f797e6a338b04e7776aa43b15b2fcc8":
                os.system("chmod +x sendEmail")
                get_cmd = "./sendEmail -f " + FROMMAIL + " -t " + DBAEMAIL + " -s " + SMTPHOST + " -u " + Title + " -xu " + FROMMAIL + " -xp " + SMTPASS + " -m 你的密码是%s" % user_pwd
                res = os.system(get_cmd)
                if res == 0:
                    logging.info("发送邮件成功")
                else:
                    logging.error("发送邮件失败")
            else:
                logging.error("下载sendMail失败")
    except Exception as e:
        logging.error(e, "发送邮件有问题")


def send_mail2(obj):
    """
    this is a function of send mail with use Python
    obj is list
    :return:
    """
    # 第三方 SMTP 服务
    mail_host = "smtp.163.com"  # 设置服务器
    mail_user = "test@163.com"  # 邮箱用户名
    mail_pass = "xxxxxx"  # 授权码

    sender = 'test@163.com'  # 发件人

    receivers = []  # 接收人列表
    receivers.append(obj[2])

    context = "您好: \n \n\n您的账号已开通, 可使用该账号登录服务器\n" \
    "服务器地址为: x.x.x.x, 端口为x\n" \
    "账号为: %(user)s, 密码为%(pwd)s"%{'user': obj[0], 'pwd': obj[1]}

    message = MIMEText(context, 'plain', 'utf-8')
    subject = '账号开通通知'
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = sender
    message['To'] = receivers[0]

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.connect(mail_host)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        logging.info("邮件发送成功")
    except smtplib.SMTPException as e:
        logging.error(e, "Error: 无法发送邮件")


if __name__ == "__main__":
    lst = get_up()
    open_passwd(lst)

    # # send_mail1参数
    # FROMMAIL = "xxx"
    # SMTPASS = "xxx"
    # DBAEMAIL = name_mail
    # SMTPHOST = "smtp@163.com"
    # Title = "账号开通通知"
