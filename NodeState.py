#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from conf import *



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

    ndstxml = NodeStateXML(filename=xmlfilename, nodeID=nodeID, wwwroot=wwwroot, posturl=postUrl, port=port)
    ndst = NodeState(interval=interval, mountpoint=mountpoint, device=device, netcard=netcard,bandwidth_max=bandwidth_max,conn_max=conn_max, psname=psname)
            
    ndst.set_interval(interval=1)
    while 1:    
        try:
            #get_io should be called first
            dkread, dkwrite, netsent, netrecv = ndst.get_io()
            
            ndstxml.setBWMax(str(ndst.get_bwmax()))
            ndstxml.setBWNow(str(ndst.get_netbw()))

            ndstxml.setConnNow(str(ndst.get_connections()))
            ndstxml.setConnMax(str(ndst.get_conn_max()))
	    ndstxml.setCPULoadavg(str(ndst.get_cpu_loadavg()))

            ndstxml.setCPUAverageRatio(str(ndst.get_cpuusage()))
            ndstxml.setCPUPeakRatio(str(ndst.get_cpupeak_ratio()))
            ndstxml.setmemAverageRatio(str(ndst.get_memusage()))
            ndstxml.setmemPeakRatio(str(ndst.get_mempeak_ratio()))

            ndstxml.setnorthboundConcurrencies(str(ndst.get_north_concurrencies()))
            ndstxml.setsouthboundConcurriencies(str(ndst.get_south_concurrencies()))
            ndstxml.setnorthboundIdleBW(str(ndst.get_netrecv_idle()))
            ndstxml.setsouthboundIdleBW(str(ndst.get_netsent_idle()))

            ndstxml.setidleDiskSpace(str(ndst.get_diskfree()))
            ndstxml.setDiskIORBw(str(dkread))
            ndstxml.setDiskIOWBw(str(dkwrite))
            ndstxml.settimeStamp(str(time.time()))
            ndstxml.setHostIP() 
	    ndstxml.setWeight(str(weight))
            ndstxml.setNodeStatus('0')#0: 正常
            ndstxml.writeToFile()
            
            #print ndstxml.tostring()
            ndstxml.postToServer()            
            ndst.set_interval(interval)

            logger.info("xmlstring: %s", ndstxml.tostring());
        except Exception as exc:
            print "Exception: %s while checking node state" % exc
            logger.error("Exception: %s while checking node state", exc)
            time.sleep(interval)        


if __name__ == '__main__':
    while 1:
        try:
            #main would never exit unless something unknown error
            main()
        except Exception as exc:
            print "Exception: %s while main function" % exc
            logger = logging.getLogger()
            logger.error("Exception: %s while main function", exc)
        time.sleep(interval)
