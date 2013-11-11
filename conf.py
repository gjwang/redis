# -*- coding: utf-8 -*- 

'''
Created on 2013年10月29日

@author: gjwang
'''

nodeID = 'jx_ja'
interval = 10
mountpoint = '/data'
device = None #device='/dev/sda9'
netcard = 'eth0'
psname = 'ngnix'
postUrl = 'http://127.0.0.1/getnodestate'
wwwroot = '/data/ysten'
xmlfilename="NodeState.xml"
logfilename = "log/nodestate.log"


REDIS_MEDIA_DATA_DB = 0

REDIS_MD_CONFIG = {
    "server": "127.0.0.1",
    "port": 6379,
    "db": REDIS_MEDIA_DATA_DB,
}
