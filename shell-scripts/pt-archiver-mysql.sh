#!/bin/bash
# 使用此脚本的前提,先安装pt-archiver
# Author: congyang
# Date: 2019/5/21

# SOURCE
MYSQLHOST="localhost"
MYSQLUSER="congy"
MYSQLPASSWD="congy"
SOURCEDB="test"
SOURCETBL=$1
# DEST
KEEP_DAY=6
DESTDB="testbackup"
CONDITION_DATA=`date -d "$(date +%Y%m01) ${KEEP_DAY} month ago" +'%Y%m%d'`
CONDITION_COLUMN="start_time"
DESTTBL="${SOURCETBL}_${CONDITION_DATA}"
table1="CREATE TABLE \`${DESTTBL}\` (\`id\` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增id',) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
table2="CREATE TABLE \`${DESTTBL}\` (\`id\` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增id',) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"


BASEMYSQL="`ps -ef | grep mysql | awk -F ' ' '{for (f=1; f <= NF; f+=1) {if ($f ~ /basedir/) {print substr($f, 11)}}}'`"
PORT="`ps -ef | grep mysql | awk -F ' ' '{for (f=1; f <= NF; f+=1) {if ($f ~ /port/) {print substr($f, 8)}}}'`"
SOCKET="`ps -ef | grep mysql | awk -F ' ' '{for (f=1; f <= NF; f+=1) {if ($f ~ /socket/) {print substr($f, 10)}}}'`"
MYSQLCLI="${BASEMYSQL}/bin/mysql"
LOG_PATH="./logs"
LOG_FILE="${LOG_PATH}/${SOURCEDB}-${DESTTBL}-${CONDITION_DATA}.log"

MYSQL_S_CMD="h=${MYSQLHOST},u=${MYSQLUSER},p=${MYSQLPASSWD},P=${PORT},D=${SOURCEDB},t=${SOURCETBL}"
MYSQL_D_CMD="h=${MYSQLHOST},u=${MYSQLUSER},p=${MYSQLPASSWD},P=${PORT},D=${DESTDB},t=${DESTTBL}"

# pt-archiver路径
PTAR="/usr/bin/pt-archiver"

NOW_TIME=`date +"%F %T"`

# 使用root
if [ $(id -u) != 0 ]; then
    echo -e "\033[43;30mPermission denied ! Please use root user\033[0m"
    exit 1
fi

# 
if [ "$#" -ne "1" ]; then
	echo -e "\033[43;30m请按照 [ sudo sh $0 备份的表 ] 格式执行脚本\033[0m"
        exit 1
fi


# 日志目录
if [ ! -d ${LOG_PATH} ];then
    mkdir ${LOG_PATH} -p
fi

getcmd(){
echo "will done: $1"
RESULT=`${MYSQLCLI} -h${MYSQLHOST} -P${PORT} -u${MYSQLUSER} -p${MYSQLPASSWD} --socket=${SOCKET} -N -e "$1"`
if [ $? -ne 0 ];then
        echo "[${NOW_TIME}] [ERROR] 下列命令执行失败！" |tee -a $LOG_FILE
        echo "$1" |tee -a $LOG_FILE
        return 1
fi
        echo "[${NOW_TIME}] [INFO] 下列命令执行成功！" |tee -a $LOG_FILE
        echo "$1" |tee -a $LOG_FILE
        echo "执行结果为" |tee -a $LOG_FILE
        echo "result: $RESULT" |tee -a $LOG_FILE
}

# 判断是否存在目标库
${MYSQLCLI} -h${MYSQLHOST} -P${PORT} -u${MYSQLUSER} -p${MYSQLPASSWD} --socket=${SOCKET} -N -e "show databases" | grep "${DESTDB}"
if [ $? = 0 ];then
    echo "[${NOW_TIME}] [INFO] ${DESTDB}数据库存在" |tee -a $LOG_FILE
else
    echo "[${NOW_TIME}] [ERROR] ${DESTDB}数据库不存在" |tee -a $LOG_FILE
    exit 1
fi

# 判断是否存在目标表
biao_sql="SELECT table_name FROM information_schema.TABLES WHERE table_name = '${DESTTBL}'"
res=`${MYSQLCLI} -h${MYSQLHOST} -P${PORT} -u${MYSQLUSER} -p${MYSQLPASSWD} --socket=${SOCKET} -N -e "${biao_sql}" | wc -c`
if [ ${res} -gt 1 ];then
    echo "[${NOW_TIME}] [INFO] ${DESTDB}.${DESTTBL}数据表存在" |tee -a $LOG_FILE
else
    echo "[${NOW_TIME}] [ERROR] ${DESTDB}.${DESTTBL}数据表不存在, 正在创建" |tee -a $LOG_FILE
    if [ "${SOURCETBL}" = "table1" ]
    then
        DESTTBL_SQL="${table1}"
        getcmd "USE ${DESTDB}; ${DESTTBL_SQL}"|| exit 1
        echo "[${NOW_TIME}] [INFO] ${DESTDB}.${DESTTBL}数据表创建成功" |tee -a $LOG_FILE
    elif [ "${SOURCETBL}" = "table2" ]
        DESTTBL_SQL="${table2}"
        getcmd "USE ${DESTDB}; ${DESTTBL_SQL}"|| exit 1
        echo "[${NOW_TIME}] [INFO] ${DESTDB}.${DESTTBL}数据表创建成功" |tee -a $LOG_FILE
    else
        echo "[${NOW_TIME}] [ERROR] 输入的${SOURCETBL}数据表不存在, 请检查" |tee -a $LOG_FILE
        exit 1
    fi
fi

# 原表数据
count_sql="select count(id) from ${SOURCEDB}.${SOURCETBL} WHERE ${CONDITION_COLUMN} < '${CONDITION_DATA}'"
getcmd "${count_sql}"|| exit 1
count=$RESULT
echo "[${NOW_TIME}] [INFO] ${SOURCEDB}库${SOURCEDBTBL}表的${CONDITION_COLUMN} < ${CONDITION_DATA}的将会删除${count}..." |tee -a $LOG_FILE
echo "##################################################################" |tee -a $LOG_FILE
echo "[${NOW_TIME}] [INFO] 开始执行 ${PTAR} --source ${MYSQL_S_CMD} --dest ${MYSQL_D_CMD} --no-check-charset --where \"${CONDITION_COLUMN}<'${CONDITION_DATA}'\" --progress 5000 --limit=5000 --txn-size 5000 --bulk-insert --statistics --bulk-delete" |tee -a $LOG_FILE
${PTAR} --source ${MYSQL_S_CMD} --dest ${MYSQL_D_CMD} --no-check-charset --where "${CONDITION_COLUMN}<'${CONDITION_DATA}'" --progress 5000 --limit=5000 --txn-size 5000 --bulk-insert --statistics --bulk-delete |tee -a $LOG_FILE
if [ $? -eq 0 ];then
    # 目标表数据
    count_sql="select count(id) from ${DESTDB}.\`${DESTTBL}\` WHERE ${CONDITION_COLUMN} < '${CONDITION_DATA}'"
    getcmd "${count_sql}"|| exit 1
    count=$RESULT
    echo "[${NOW_TIME}] [INFO] ${DESTDB}库${DESTTBL}表的${CONDITION_COLUMN} < ${CONDITION_DATA}的将会增加${count}..." |tee -a $LOG_FILE
fi
