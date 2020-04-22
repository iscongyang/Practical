# -*- coding: utf-8 -*
#!/usr/bin/env python3
import os
import paramiko

class SftpFile:

    def __init__(self,ssh_host,ssh_port,ssh_uname,ssh_pw):

        self.conn = paramiko.Transport((ssh_host,ssh_port))
        self.conn.connect(username=ssh_uname,password=ssh_pw)

    def put_path(self,l_path,r_path):
        sftp = paramiko.SFTPClient.from_transport(self.conn)
        for file in os.listdir(l_path):
            remeto_file = r_path + "/" + l_path + "/" + file
            try:
                sftp.listdir(os.path.join(r_path,l_path))
                sftp.put(os.path.join(l_path, file), remeto_file)
            except:
                sftp.chdir(r_path)
                sftp.mkdir(l_path)
                sftp.put(os.path.join(l_path, file), remeto_file)

    def  put_file(self,l_file,r_path):
        sftp = paramiko.SFTPClient.from_transport(self.conn)
        remote_file = r_path + l_file
        try:
            sftp.put(l_file,remote_file)
        except:
            print('传输失败！')