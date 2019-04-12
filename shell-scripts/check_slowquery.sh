#!/bin/bash

#source  ./fun_mail.sh

USERNAMW=root
PASSWORD=root
PORT=3306
DBHOST=localhost
MYSQLBASEDIR=/usr/local/platform/mysql/mysql57
SOCKET="/usr/local/platform/mysql/mysql_tmp/mysql.sock"
NUM=3
#DBAEMAIL="iscongyang@163.com"
LOG_PATH=/tmp/t.log

MYSQLDIR=${MYSQLBASEDIR}/bin/mysql
MYSQLDUMPSLOW=${MYSQLBASEDIR}/bin/mysqldumpslow

function getcmd()
{
    echo "will done: $1"
    RES=`${MYSQLDIR} -u${USERNAMW} -p${PASSWORD} -h${DBHOST} -P${PORT} --socket=${SOCKET} -e "$1" | xargs | awk '{print $NF}'`
    if [ $? -eq 0 ]
    then
	echo "[$(date "+%F %T")] [INFO] 下列命令执行成功！"
        echo "$1"
        echo "执行结果为"
        echo "result: $RES "
    else
	echo "[$(date "+%F %T")] [ERROR] 下列命令执行失败！"
        echo "$1"
	exit 1
    fi
}

slow_query_file_sql="show variables like 'slow_query_log_file'"
getcmd "${slow_query_file_sql}" || exit 1
slow_query_file=$RES
echo "慢查询日志位置是: ${slow_query_file}" |tee -a $LOG_PATH

slow_query_time_sql="show variables like 'long_query_time'"
getcmd "${slow_query_time_sql}" || exit 1
slow_query_time=$RES
echo "慢查询设置时间是: ${slow_query_time}" |tee -a $LOG_PATH

echo "----------------------------------------------------------" |tee -a $LOG_PATH
echo "平均查询时间最多的${NUM}条语句: " |tee -a $LOG_PATH
${MYSQLDUMPSLOW} -s at -t $NUM -a ${slow_query_file} |tee -a $LOG_PATH
echo "----------------------------------------------------------"|tee -a $LOG_PATH
echo "平均锁定时间最多的${NUM}条语句: " |tee -a $LOG_PATH
${MYSQLDUMPSLOW} -s al -t $NUM -a ${slow_query_file} |tee -a $LOG_PATH
echo "----------------------------------------------------------"|tee -a $LOG_PATH
echo "平均返回记录时间最多的${NUM}条语句: " |tee -a $LOG_PATH
${MYSQLDUMPSLOW} -s ar -t $NUM -a ${slow_query_file} |tee -a $LOG_PATH

#mailfun "Check OK!"
