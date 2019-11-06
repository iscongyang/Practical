#!/bin/bash

###sftp_dir owner and group will be changed to root:root
sftp_dir="/usr/local/sftp"
sftp_user="xxx"
user_passwd="xxxx"
config_status=`cat /etc/ssh/sshd_config | grep "Match Group sftp" | wc -l`
group_status=`cat /etc/group | grep -E '^sftp:' | wc -l`
user_status=`cat /etc/passwd | grep -E '^'$sftp_user: | wc -l`

echo "sftp install program is starting"

#config sftp
if [[ $config_status == 0 ]];then
    echo "---config sshd_config and restart sshd"
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config_back
    sed -i 's/^Subsystem/#Subsystem/g' /etc/ssh/sshd_config 
    tee -a /etc/ssh/sshd_config <<EOF
Subsystem   sftp    internal-sftp
Match Group sftp
        X11Forwarding no
        ChrootDirectory ${sftp_dir}/%u
        AllowTcpForwarding no
        ForceCommand internal-sftp
EOF
    service sshd restart
fi

#add sftp group
if [[ 0 == $group_status ]];then
    echo "---add sftp group: sftp"
    groupadd sftp
fi

#add sftp user
if [[ 0 == $user_status ]];then
    echo "---add sftp user: ${sftp_user}"
    useradd -g sftp -s /sbin/nologin $sftp_user
    echo $user_passwd | passwd --stdin $sftp_user >/dev/null 2>&1 &
fi

#mkdir
if [[ ! -d $sftp_dir/$sftp_user/download ]];then
    echo "---mkdir for sftp user and change dir owner and group"
    mkdir -p $sftp_dir/$sftp_user/download
    chown root:sftp $sftp_dir/$sftp_user
    chown $sftp_user:sftp $sftp_dir/$sftp_user/download
fi

#Change folder properties
echo "---chmod sftp root dir and change dir owner and group"
floder=""
OLD_IFS="$IFS"
IFS="/"
arr=($sftp_dir)
IFS="$OLD_IFS"
for s in ${arr[@]}
do
    floder="$floder/$s"
    chmod 755 $floder
    chown root:root $floder
done

echo "Sftp installed successfully!"
echo "User: $sftp_user"
echo "Dir: $sftp_dir/$sftp_user"
