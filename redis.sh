#!/bin/sh 
# 
# Script to start Redis and promote to MASTER/SLAVE 
 
# Usage Options: 
#   -m    promote the redis-server to MASTER 
#   -s    promote the redis-server to SLAVE 
#   -k    start the redis-server and promote it to MASTER 
# 
REDIS_HOME="/usr/local/bin" 
REDIS_COMMANDS="/usr/local/bin"                # redis执行文件的目录 
REDIS_MASTER_IP="127.0.0.1"                  # Redis MASTER ip 
REDIS_MASTER_PORT="6379"                        # Redis MASTER port 
REDIS_CONF="/etc/keepalived/keepalived.conf"                     # 配置文件 
 
E_INVALID_ARGS=65 
E_INVALID_COMMAND=66 
E_NO_SLAVES=67 
E_DB_PROBLEM=68 
 
error() { 
        E_CODE=$? 
        echo "Exiting: ERROR ${E_CODE}: $E_MSG" 
 
        exit $E_CODE 
} 
 
start_redis() { 
      alive=`${REDIS_COMMANDS}/redis-cli PING` 
      if [ "$alive" != "PONG" ]; then 
        ${REDIS_COMMANDS}/redis-server ${REDIS_HOME}/${REDIS_CONF} 
        sleep 1 
      fi 
} 
 
start_master() { 
        ${REDIS_COMMANDS}/redis-cli SLAVEOF no one 
} 
 
start_slave() { 
        ${REDIS_COMMANDS}/redis-cli SLAVEOF ${REDIS_MASTER_IP} ${REDIS_MASTER_PORT} 
} 
 
usage() { 
        echo -e "Start Redis and promote to MASTER/SLAVE - version 0.3 (c) Alex Williams - www.alexwilliams.ca" 
        echo -e "\nOptions: " 
        echo -e "\t-m\tpromote the redis-server to MASTER" 
        echo -e "\t-s\tpromote the redis-server to SLAVE" 
        echo -e "\t-k\tstart the redis-server and promote it to MASTER" 
        echo -e "" 
 
        exit $E_INVALID_ARGS 
} 
 
for arg in "$@" 
do 
        case $arg in 
        -m) arg_m=true;; 
        -s) arg_s=true;; 
        -k) arg_k=true;; 
        *) usage;; 
        esac 
done 
 
if [ $arg_m ]; then 
        echo -e "Promoting redis-server to MASTER\n" 
        start_redis 
        wait 
        start_master 
elif [ $arg_s ]; then 
        echo -e "Promoting redis-server to SLAVE\n" 
        start_redis 
        wait 
        start_slave 
elif [ $arg_k ]; then 
        echo -e "Starting redis-server and promoting to MASTER\n" 
        start_redis 
        wait 
        start_master 
else 
        usage 
fi 
