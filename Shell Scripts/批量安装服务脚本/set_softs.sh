#!/bin/bash

# 修改系统参数
function set_systemconf() {
   sed -i "s/enforcing/disabled/g" /etc/selinux/config
   setenforce 0
   cat >> /etc/sysctl.conf << EOF
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_max_tw_buckets = 55000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1100 65535
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 200000
net.core.rmem_default = 262144
net.core.wmem_default = 262144
net.core.rmem_max = 2097152
net.core.wmem_max = 2097152
net.ipv4.ip_forward = 1
net.ipv4.conf.default.rp_filter = 0
net.ipv4.conf.all.rp_filter = 0
net.ipv4.conf.default.arp_announce = 2
net.ipv4.conf.lo.arp_announce=2
net.ipv4.conf.all.arp_announce=2
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syncookies = 1
vm.swappiness = 0
kernel.sysrq = 1
vm.max_map_count = 262144
EOF
    echo -e "root soft nofile 65535\nroot hard nofile 65535\n* soft nofile 65535\n* hard nofile 65535" >> /etc/security/limits.conf
    echo "DefaultLimitNOFILE=65535" >> /etc/systemd/system.conf
    systemctl daemon-reload
	systemctl stop firewalld.service
	systemctl disable firewalld.service
}

# set JAVAHOME
function set_javahome() {
    javah=$(readlink -f `which java` | awk -F '/jre' '{print $1}')
    cat > /etc/profile.d/java.sh << EOF
JAVA_HOME=$javah
PATH=\$JAVA_HOME/bin:\$PATH
export JAVA_HOME
export PATH
EOF
    source /etc/profile
}

# 设置Nginx配置文件,Nginx自启动
function set_nginx()
{
    cat > /etc/nginx/nginx.conf << EOF
worker_processes  1;
pid        /var/run/nginx.pid;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    server {
        listen       80;
        server_name  localhost;
		root /app;
		index index.html index.htm index.php;
 
		location / {
			try_files \$uri @rewrite;
		}		 
		location @rewrite {
			set \$static 0;
			if (\$uri ~ \.(css|js|jpg|jpeg|png|gif|ico|woff|eot|svg|css\.map|min\.map)\$) {
				set \$static 1;
			}
			 
			if (\$static = 0) {
				rewrite ^/(.*)\$ /spms/index.php?s=/\$1;
			}
		 
		}		 
		location ~ /Uploads/.*\.php\$ {
			deny all;
		}		 
		location ~ \.php/ {
			if (\$request_uri ~ ^(.+\.php)(/.+?)(\$|\?)) { }
			fastcgi_pass  127.0.0.1:9000;
			include fastcgi_params;
			fastcgi_param SCRIPT_NAME \$1;
			fastcgi_param PATH_INFO \$2;
			fastcgi_param SCRIPT_FILENAME \$document_root\$1;
			#fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
		}		 
		location ~ \.php\$ {
			fastcgi_pass 127.0.0.1:9000;
			fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
			include fastcgi_params;
		}
		location ~ /\.ht {
			deny all;
		}
    }
}
EOF
    systemctl restart nginx
    systemctl enable nginx
}

# 设置数据库
function set_database() {
    systemctl start mysqld.service
    # 修改密码
    mysql -uroot --connect-expired-password -p$(grep 'temporary password' /var/log/mysqld.log | awk -F": " '{print $NF}') -e"set password=password('xxx');"
    rand=$(echo $RANDOM)
    # 修改配置文件
    cat > /etc/my.cnf << EOF
[mysqld]
user = mysql
datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
symbolic-links=0
server_id = $rand
log-error=/var/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid
innodb_buffer_pool_size = 128M
character_set_server=utf8mb4
explicit_defaults_for_timestamp = 1
event_scheduler = 1
interactive_timeout = 7200
wait_timeout = 7200
lock_wait_timeout = 1800
skip_name_resolve = 1
max_connections = 1024
log_bin = binlog
expire_logs_days = 10
innodb_flush_method = O_DIRECT
innodb_log_file_size = 1G
innodb_print_all_deadlocks = 1
innodb_file_per_table = 1
binlog_format = ROW
log_timestamps = system
show_compatibility_56 = on
innodb_buffer_pool_load_at_startup = 1
innodb_buffer_pool_dump_at_shutdown = 1
sql_mode=STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
lower_case_table_names = 1
EOF
    # root@127.0.0.1用户授权
    mysql -uroot -p"xxx*(" -e "grant all privileges on *.* to root@'%' identified by 'xxx' with grant option"
    # 导入数据库
    mysql -uroot -p"xxx*(" < /root/park/parking.sql
    systemctl restart mysqld.service
    systemctl enable mysqld.service
}

# 设置Supervisor, 配置Java程序
function set_supervisor() {
    # 放置Java程序
    mv /root/park/Mscommon /app/mscommon
    # 设置supervisor的conf
	echo "files = supervisord.d/*.conf" >> /etc/supervisord.conf
	cat > /etc/supervisord.d/mscommon.conf << EOF
[program:mscommon]
command=xxx # Java启动命令
directory=/app/mscommon
stdout_logfile=/app/mscommon/logs/mscommon.log
redirect_stderr=true
startsecs=0
stopwaitsecs=600
user=root
autostart=true
autorestart=true
EOF
	systemctl start supervisord
    systemctl enable supervisord
	supervisorctl start mscommon
}

# 设置docker程序
function set_docker() {
    systemctl daemon-reload
    systemctl start docker
    docker load < /root/park/parking_charge_tool_0.0.1.tar  #加载docker程序
    docker run -d --network=host --restart always -v /app/logs:/app/charge_tool/logs --env mysql_host=127.0.0.1 --env mysql_pwd='xxx' [docker image]
    systemctl enable docker
}

# 设置PHP程序
function set_php() {
    mv /root/park/spms /app/
    systemctl start php-fpm
    systemctl enable php-fpm
}

# 调用函数
set_systemconf
set_javahome
set_nginx
set_database
set_supervisor
set_docker
set_php
