#!/bin/bash

#set -e 

. /etc/init.d/functions

installs_soft=(
perl libaio net-tools ntpdate yum-utils device-mapper-persistent-data lvm2
java-1.8.0-openjdk java-1.8.0-openjdk-devel
mysql-community-server
nginx-1:1.16.1-1.el7.ngx.x86_64
php70w* php70w-fpm php70w-opcache
docker-ce
supervisor
)

# 安装软件
function install_softwares() {
    for ((i=0;i<${#installs_soft[@]};i++)) ; do
        yum install ${installs_soft[i]} -y
        if [ $? == 0 ];then
            action "install Successful" /bin/true
        else
            action "install Failed, Please Check! " /bin/false
            exit 1
        fi 
    done
	#运行设置脚本
	sh ./set_softs.sh
}

function final(){
    # 同步时间
	echo "00 1 * * *  ntpdate time1.aliyun.com"  >> /tmp/crontab.add
	echo "00 2 * * *  /usr/bin/echo > /app/logs/charge_tool.log"  >> /tmp/crontab.add
	crontab /tmp/crontab.add
	ntpdate time1.aliyun.com
    # 恢复repo
    mv /etc/yum.repos.d/old/* /etc/yum.repos.d/
    rm -rf /etc/yum.repos.d/old
    rm -rf /etc/yum.repos.d/park.repo
	# 运行sftp脚本
    sh ./sftp_install.sh
    echo "数据库密码为:xxx"
}

function check_env() {
    # check user
    if [ `id -u` != 0 ]
    then
        echo -e "\033[43;30mPermission denied ! Please use root user\033[0m"
        exit 1
    fi
	# 解压park包
    tar -zxvf /root/park/park.tgz
    mkdir /app -p
	mkdir /app/logs -p
    mkdir /etc/yum.repos.d/old -p
    mv /etc/yum.repos.d/*.* /etc/yum.repos.d/old/
    cat > /etc/yum.repos.d/park.repo << EOF
[park]
name=park
baseurl=file:///root/park/park
gpgcheck=0
enabled=1
EOF
	# 清空yum
    yum clean
    yum makecache
    
}

 function main()
{
    check_env
    install_softwares
    final
}

main