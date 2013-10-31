# -*- coding: utf-8 -*- 

'''
Created on 2013年10月29日

@author: gjwang
'''

import redis
import time
from conf import *

#redis_connection_pool = redis.ConnectionPool(host=REDIS_MD_CONFIG['server'], port=REDIS_MD_CONFIG['port'], db=REDIS_MD_CONFIG['db'])
#redisConn = redis.Redis(socket_timeout=5, connection_pool=redis_connection_pool)
redisConn = redis.Redis(host=REDIS_MD_CONFIG['server'], port=6379, db=0, password=None, socket_timeout=5)


redisConn.set('foo', 0)

i = 0
while 1:
    i += 1

    try:
        redis_id = redisConn.get('redisid')
	val = redisConn.get('foo')
	print "rid:%s, %s" % (redis_id, val)
	val = int(val) + 1
        redisConn.set('foo', val )
    except Exception as exc:
        print "Exception: %s" % exc
	break

    #time.sleep(0.1)

