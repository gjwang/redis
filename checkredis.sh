#!/bin/bash 
REDIS_HOME="/usr/local/bin" 
REDIS_COMMANDS="/usr/local/bin"      # The location of the redis binary 
REDIS_MASTER_IP="127.0.0.1"                  # Redis MASTER ip 
REDIS_MASTER_PORT="6379"                        # Redis MASTER port 
 
ERROR_MSG=`${REDIS_COMMANDS}/redis-cli PING` 
 
# 
# Check the output for PONG. 
# 
if [ "$ERROR_MSG" != "PONG" ] 
then 
        # redis is down, return http 503 
        /bin/echo -e "HTTP/1.1 503 Service Unavailable\r\n" 
        /bin/echo -e "Content-Type: Content-Type: text/plain\r\n" 
        /bin/echo -e "\r\n" 
        /bin/echo -e "Redis is *down*.\r\n" 
        /bin/echo -e "\r\n" 
        exit 1 
else 
        # redis is fine, return http 200 
        /bin/echo -e "HTTP/1.1 200 OK\r\n" 
        /bin/echo -e "Content-Type: Content-Type: text/plain\r\n" 
        /bin/echo -e "\r\n" 
        /bin/echo -e "Redis is running.\r\n" 
        /bin/echo -e "\r\n" 
        exit 0 
fi 

