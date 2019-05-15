#!/bin/bash

USER=$1
# this is user key
KEYS="...."


function tailer() {
    usermod -a -G tomcat ${USER}
    echo "123456Qq!" | passwd --stdin ${USER}
    temp3=`id ${USER} | grep tomcat | wc -l`
    if [ ${temp3} = 1 ] ;then
        echo "tomcat权限添加成功"
    else
        echo "用户tomcat组添加失败"
    fi
    chown -R ${USER}.${USER} /home/${USER}
    service sshd reload
    if [ $? -eq 0 ] ; then
        echo "${USER}可以登录"
    else
        echo "${USER}登录失败"
        exit 1
    fi
}


function AppendSudo() {
    read -p "是否给${USER}授予SUDO登录权限[y/n]:" a
    if [ "${a}" = "y" ]; then
        issudo=$(id ${PLAYUSER} | grep wheel | wc -l)
        if [ ${issudo} = 1 ]; then
            usermod -a -G wheel ${USER}
            if [ $? -eq 0 ]; then
                echo "添加sudo成功"
            else
                echo "添加sudo失败"
                exit 1
            fi
        else
            num=`cat /etc/sudoers | grep -n "^${PLAYUSER}" | awk -F ":" '{print $1}'`
            dai="${USER}   ALL=(ALL)      ALL"
            sed "${num}a ${dai}" /etc/sudoers -i
            if [ $? -eq 0 ] ; then
                echo "添加sudo权限成功"
                cat /etc/sudoers | grep 'ALL=(ALL)' | grep -v '^#'
            else
                echo "添加sudo权限失败"
                cat /etc/sudoers | grep 'ALL=(ALL)' | grep -v '^#'
                exit 1
            fi
        fi
    fi
}


function AppendSSH() {
    read -p "是否给${USER}授予SSH登录权限[y/n]:" a
    if [ "${a}" = 'y' ]; then
        temp=$(cat /etc/ssh/sshd_config | grep -w "AllowUsers")
        sed -i "s/${temp}/${temp} ${USER}/g" /etc/ssh/sshd_config
        if [ $? -eq 0 ]; then
	        temp2=`cat /etc/ssh/sshd_config | grep -w "AllowUsers"`
            echo "添加SSH成功, 显示 -> ${temp2}"
        else
            echo "添加SSH失败"
            exit 1
        fi
    else
	    echo "不给SSH权限"
        exit 1
    fi
}


function USERADD() {
    useradd ${USER}
    mkdir /home/$USER/.ssh -p
    echo ${KEYS} >/home/${USER}/.ssh/authorized_keys
    if [ $? -eq 0 ]; then
	    chmod 400 /home/${USER}/.ssh/authorized_keys
	    chmod 700 /home/$USER/.ssh
	    echo "添加用户成功"
    else
        echo "添加用户失败"
        exit 1
    fi
}


function PanDuan() {
    if [ $(id -u) != 0 ]; then
        echo -e "\033[43;30mPermission denied ! Please use root user\033[0m"
        exit 1
    fi

    id ${USER}
    if [ $? -eq 0 ]; then
	    echo "此用户已存在"
	    exit 1
    else
        USERADD
    fi
}


function main()
{
PanDuan
AppendSSH
AppendSudo
tailer
}


if [ "$#" -ne "1" ]; then
	echo -e "\033[43;30m请按照 [ sudo sh $0 username ] 格式执行脚本\033[0m"
        exit 1
fi

read -p '请输入你的身份：' PLAYUSER
id ${PLAYUSER}
if [ $? -ne 0 ]; then
    #action "此用户已存在" /bin/true
    echo "请输入正确的用户"
    exit 1
fi

main 
