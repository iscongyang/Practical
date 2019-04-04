#!/bin/bash
 #Author: congyang
 #Time:2019-04-03 21:55:58
 #Version: V1.0
 #Description: This is a script to install nginx , you only need to change some of these parameters

. /etc/init.d/functions

# Choose your own version
DESTDIR=tengine-2.3.0 

# Choose your own installation directory
DESTPATH=/usr/local/platform/tengine

PNAME=${DESTDIR}.tar.gz

# Note that the download address does not expire
PURL=http://tengine.taobao.org/download/${PNAME}

function PanDuan()
{
if [ `id -u` != 0 ]
then
	echo -e "\033[43;30mPermission denied ! Please use root user\033[0m"
	exit 1
fi

NG=$(ps -ef |grep nginx |grep -v grep|wc -l) 
if [ ${NG} -ge "2" ]
then
	echo -e "\033[43;30mNginx is running, Can't install\033[0m"
        exit 1
fi
}

function DownPackage()
{
	wget -c "${PURL}"
	if [ "$?" == 0 ]
	then
		tar -zxvf ./${PNAME} &> /dev/null
		if [ "$?" == 0 ]
		then
			/bin/ls ${DESTPATH} &> /dev/null
			if [ "$?" != 0 ]
			then
				cd ./${DESTDIR}
				echo "./configure --prefix=${DESTPATH}"
				./configure --prefix=${DESTPATH}
				echo "make && sudo make install"
				make && sudo make install &>/dev/null
				if [ "$?" == 0 ]
				then
					action "${DESTDIR} install Successful" /bin/true
				else
					action "${DESTDIR} install Failed, Please Check!!!" /bin/false
				fi
			else
				action "${DESTPATH} is exists, Please Check!!!" /bin/false
				exit 1
			fi
		else
			action "NOT Extract the file ${PNAME} , Please Check!!!" /bin/false
			exit 1
		fi
	else
		action "${PNAME} download Failed, Please Check!!!" /bin/false
		exit 1
	fi
}

function CheckEnv()
{
# check environment is installed
installs=( gcc zlib zlib-devel pcre-devel openssl openssl-devel )
for ((i=0; i<${#installs[@]}; i++))
do
	rpm -qa | grep '^${installs[i]}'
	if [ "$?" == "0" ]; then
       	action "${installs[i]} is exists" /bin/true
	else
		yum install ${installs[i]} -y &> /dev/null
       		if  [ "$?" == "0" ]; then
             		action "${installs[i]} install Successful" /bin/true
       		else
  			action "${installs[i]} install Failed" /bin/false
  			exit 1
  		fi
	fi
done
}

function AutoStart()
{
cat >/etc/init.d/nginx<<EOF
#!/bin/bash
#
# nginx - this script starts and stops the nginx daemon
#
# chkconfig: - 85 15
# description: Nginx is an HTTP(S) server, HTTP(S) reverse
# proxy and IMAP/POP3 proxy server
# processname: nginx
# config: /etc/nginx/nginx.conf
# config: /etc/sysconfig/nginx
# pidfile: /var/run/nginx.pid
# Source function library.
. /etc/rc.d/init.d/functions
# Source networking configuration.
. /etc/sysconfig/network
# Check that networking is up.
[ "\$NETWORKING" = "no" ] && exit 0
TENGINE_HOME="${DESTPATH}/"
nginx=\$TENGINE_HOME"sbin/nginx"
prog=\$(basename \$nginx)
NGINX_CONF_FILE=\$TENGINE_HOME"conf/nginx.conf"
[ -f /etc/sysconfig/nginx ] && /etc/sysconfig/nginx
lockfile=/var/lock/subsys/nginx
start() {
    [ -x \$nginx ] || exit 5
    [ -f \$NGINX_CONF_FILE ] || exit 6
    echo -n \$"Starting \$prog: "
    daemon \$nginx -c \$NGINX_CONF_FILE
    retval=\$?
    echo
    [ \$retval -eq 0 ] && touch \$lockfile
    return \$retval
}
stop() {
    echo -n \$"Stopping \$prog: "
    killproc \$prog -QUIT
    retval=\$?
    echo
    [ \$retval -eq 0 ] && rm -f \$lockfile
    return \$retval
    killall -9 nginx
}
restart() {
    configtest || return \$?
    stop
    sleep 1
    start
}
reload() {
    configtest || return \$?
    echo -n \$"Reloading \$prog: "
    killproc \$nginx -HUP
    RETVAL=\$?
    echo
}
force_reload() {
    restart
}
configtest() {
    \$nginx -t -c \$NGINX_CONF_FILE
}
rh_status() {
    status \$prog
}
rh_status_q() {
    rh_status >/dev/null 2>&1
}
case "\$1" in
start)
    rh_status_q && exit 0
    \$1
;;
stop)
    rh_status_q || exit 0
    \$1
;;
restart|configtest)
    \$1
;;
reload)
    rh_status_q || exit 7
        \$1
;;
force-reload)
    force_reload
;;
status)
    rh_status
;;
condrestart|try-restart)
    rh_status_q || exit 0
;;
*)
echo \$"Usage: \$0 {start|stop|status|restart|condrestart|try-restart|reload|force-reload|test}"
exit 2
esac
EOF
}

function AddService()
{
	/bin/chmod u+x /etc/init.d/nginx
	/sbin/chkconfig --add nginx
	/sbin/chkconfig nginx on
	/sbin/chkconfig --list | grep nginx
	if [ "$?" == 0 ]
	then
		echo "已加入自启动"
		echo "you can execution to start NGINX ==> service nginx start"
		echo "if you want to open the filewall,you can add this rule:"
		echo "-A INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT"
	else
		echo "没有发现自启动"
		exit 1
	fi
}

function main()
{
	PanDuan
	CheckEnv
	DownPackage
	AutoStart
	AddService
}

main
