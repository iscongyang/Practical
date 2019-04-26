#!/bin/bash

if [ `id -u` != 0 ]
then
	echo -e "\033[43;30mPermission denied ! Please use root user\033[0m"
	exit 1
fi

if [ "$#" -ne "1" ]; then
    echo "请输入一个邮件接收人,如: admin@163.com"
    exit 2
fi

DBAEMAIL=$1
MYSQLBASEDIR="`ps -ef | grep mysql | awk -F ' ' '{for (f=1; f <= NF; f+=1) {if ($f ~ /basedir/) {print substr($f, 11)}}}'`"

SLOW_FILE="`find /usr/local/platform/ -type f -name 'slow_queries.log'`"
if [ $? -eq 0 ];then
        SLOW_DIR="`echo ${SLOW_FILE} | sed 's#slow_queries.log##g'`"
        if [ $? -eq 0 ];then
                SLOW_OLD="${SLOW_DIR}oldlogs"
                [ ! -d ${SLOW_OLD} ] && sudo -u mysql mkdir ${SLOW_OLD}
                if [ $? -eq 0 ];then
                        echo "${SLOW_OLD}创建成功"
                else
                        echo "${SLOW_OLD}已经存在或创建失败"
                        exit 1
                fi
        fi
else
        echo "没有找到慢查询日志"
        exit 1
fi

tar -zxvf ./check_slow_query.tgz
if [ $? -eq 0 ];then
	mv ./check_slow_query  /usr/local/platform/
	sudo chown -R root.root /usr/local/platform/check_slow_query/
	echo "修改权限成功"
	sudo sed -i "s#admin@163.com#${DBAEMAIL}#g" /usr/local/platform/check_slow_query/check_slow_query.sh
	echo "邮件接收人改变成功"
fi

cat >/etc/logrotate.d/mysqlslowlog << EOF
${SLOW_FILE}{

daily
rotate 35
dateext
dateformat %Y%m%d
compress
copytruncate
delaycompress
notifempty
olddir ${SLOW_OLD}
}
EOF

echo "=========================================警告线开始======================================"
echo "把以下2句放入定时任务:"
echo "0 0 * * * /usr/sbin/logrotate -f /etc/logrotate.d/mysqlslowlog > /dev/null 2>&1"
echo "50 23 * * * /bin/sh /usr/local/platform/check_slow_query/check_slow_query.sh > /dev/null 2>&1"
echo "请前往check_slow_query.sh修改mysql用户名和密码!!!"
echo "=========================================警告线结束======================================"

/bin/rm -f check_slow_query.tgz
/bin/rm -f $0
