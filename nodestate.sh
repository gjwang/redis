#!/bin/sh

# chkconfig: 2345 08 92
# description: Automatically startup tv service.

startup()
{
	python NodeState.py &	
}
shutdown()
{
	ps -ef|grep "python NodeState.py" | grep -v grep|awk '{print $2}'|xargs kill
}
case "$1" in
        start)
                startup
                ;;
        stop)
                shutdown
                ;;
        restart)
                shutdown
                startup
                ;;

        *)
                echo "Usage: {start|stop|restart}" >&2
                exit 1
                ;;
esac
exit