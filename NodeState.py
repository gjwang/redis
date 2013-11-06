#!/usr/bin/env python

'''
Created on 2013-11-05

@author: gjwang
'''
"""
1, Get the node state, 
2, Write the state to NodeState.xml and send to the server
"""

import logging
import logging.handlers
import time
from checkNodeState import  NodeState
from NodeStateXML import NodeStateXML



nodeID = 'jx_ja'
interval = 10
mountpoint = '/home'
device = None #device='/dev/sda9'
netcard = 'eth0'
psname = 'chrome'
postUrl = 'http://223.82.137.218:8088/lua'
wwwroot = '/var/www'
xmlfilename="NodeState.xml"

logfilename = "nodestate.log"

#main would never exit unless something unknown error
def main():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    log_FileHandler = logging.handlers.TimedRotatingFileHandler(filename = logfilename,
                                                                when = 'D',
                                                                interval = 1,
                                                                backupCount = 7)
    
    log_FileHandler.setFormatter(formatter)
    log_FileHandler.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_FileHandler)    

    ndstxml = NodeStateXML(filename=xmlfilename, nodeID=nodeID, wwwroot=wwwroot, posturl=postUrl)
    ndst = NodeState(interval=interval, mountpoint=mountpoint, device=device, netcard=netcard, psname=psname)
            
    ndst.set_interval(interval=1)
    while 1:    
        try:
            #print "diskfree: %s" % ndst.get_diskfree()
            #print "memusage: %s" % ndst.get_memusage()
            dkread, dkwrite, netsent, netrecv = ndst.get_io()
            #print "dkr:%s, dkw:%s, nets:%s, netr:%s" % ndst.get_io()
            
            #get_cpuusage must after get_io
            #print "cpuusage: %s" % ndst.get_cpuusage()
            #print "conns:    %s" % ndst.get_connections()

            ndstxml.setConnNow(str(ndst.get_connections()))
            ndstxml.setCPUAverageRatio(str(ndst.get_cpuusage()))
            ndstxml.setmemAverageRatio(str(ndst.get_memusage()))

            ndstxml.setnorthboundConcurrencies(str(netrecv))
            ndstxml.setsouthboundConcurriencies(str(netsent))
            ndstxml.setidleDiskSpace(str(ndst.get_diskfree()))
            ndstxml.setDiskIORBw(str(dkread))
            ndstxml.setDiskIOWBw(str(dkwrite))
            ndstxml.settimeStamp(str(time.time()))
            
            ndstxml.setNodeStatus("idle")
            ndstxml.writeToFile()

            print ndstxml.tostring()
            ndstxml.postToServer()
            
            ndst.set_interval(interval)
        except Exception as exc:
            logger.error("Exception: %s while checking node state", exc)
            print "Exception: %s while checking node state" % exc
            time.sleep(interval)        


if __name__ == '__main__':
    while 1:
        try:
            #main would never exit unless something unknown error
            main()
        except Exception as exc:
            logger.error("Exception: %s while main function", exc)
            print "Exception: %s while main function" % exc
        time.sleep(interval)
