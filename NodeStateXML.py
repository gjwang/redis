#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import socket
import urllib2
import logging
import logging.handlers

import xml.etree.cElementTree as ET


if os.name != "nt":
    import fcntl
    import struct
    def get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  # SIOCGIFADDR
                                            struct.pack('256s', ifname[:15])
                                            )[20:24]
                               )
else:
    def get_ip_address(ifname):
        return None
    print "Only surpport linux platform"

class NodeStateXML(object):
    def __init__(self, nodeID, wwwroot = '/data', filename=None, posturl=None,
                 ip = None, nodeStatus="0", 
                 #CntUserNow=0, CntUserMax=1000, BWNow=0, BWMax=1024*1024*1024/8, 
                 #CPUAverageRatio=0, CPUPeakRatio=0, memAverageRatio=0, memPeakRatio=0, 
                 #northboundIdleBW=0, northboundConcurrencies=0, southboundIdleBW=0, southboundConcurriencies=0,
                 #idleDiskSpace=0, IOWBw=0, IORBw=0,                  
                 ifname='eth0', port = '80', hostname = None, xmlUrl=None, 
                ):

        self.__logger = logging.getLogger(self.__class__.__name__)
        
        self.filename = filename
        self.posturl = posturl
        self.wwwroot = wwwroot

        self.ifname = ifname #netcard name
        if ip is None:
            ip = get_ip_address(self.ifname)
        self.ip = ip
                    
        if self.ip is not None:
            #TODO: if nodeID contains ip, skip next
            self.nodeID = '_'.join([nodeID, self.ip])
            
        self.port = port        
        if xmlUrl is not None:
            self.xmlUrl = xmlUrl
        elif hostname is not None:
            self.xmlUrl = ''.join(hostname, self.filename)
        elif self.ip is not None:
            self.xmlUrl = ''.join(['http://', self.ip, ':', self.port, '/', self.filename])
            #print self.xmlUrl
        else:
            self.xmlUrl = None


        self.__root = ET.Element("LoadStatusReportReq")
        self.__nodeLoadList = ET.SubElement(self.__root, "nodeLoadList")
        self.nodeLoad = ET.SubElement(self.__nodeLoadList, "nodeLoad")
        self.nodeLoad.set("nodeID", self.nodeID)
        self.nodeLoad.set("nodeStatus", nodeStatus)
        #self.nodeLoad.set("CntUserNow", CntUserNow)
        #self.nodeLoad.set("CntUserMax", CntUserMax)
        #self.nodeLoad.set("BWNow", BWNow)
        #self.nodeLoad.set("BWMax", BWMax)
        #self.nodeLoad.set("CPUAverageRatio", CPUAverageRatio)
        #self.nodeLoad.set("CPUPeakRatio", CPUPeakRatio)
        #self.nodeLoad.set("memAverageRatio", memAverageRatio)
        #self.nodeLoad.set("memPeakRatio", memPeakRatio)
        #self.nodeLoad.set("northboundIdleBW", northboundIdleBW)
        #self.nodeLoad.set("northboundConcurrencies", northboundConcurrencies)
        #self.nodeLoad.set("southboundIdleBW", southboundIdleBW)
        #self.nodeLoad.set("southboundConcurriencies", southboundConcurriencies)
        #self.nodeLoad.set("idleDiskSpace", idleDiskSpace)
        #self.nodeLoad.set("IOWBw", IOWBw)
        #self.nodeLoad.set("IORBw", IORBw)
        #self.nodeLoad.set("timeStamp", timeStamp)
        self.nodeLoad.set("xmlUrl", self.xmlUrl)

        self.__tree = ET.ElementTree(self.__root)

    def setNodeStatus(self, nodeStatus):
        self.nodeLoad.set("nodeStatus", nodeStatus)

    def setConnNow(self, connNow):
        self.nodeLoad.set("CntUserNow", connNow)        

    def setConnMax(self, connMax):
        self.nodeLoad.set("CntUserMax", connMax)

    def setBWNow(self, BWNow):
        self.nodeLoad.set("BWNow", BWNow)

    def setBWMax(self, BWMax):
        self.nodeLoad.set("BWMax", BWMax)

    def setCPUAverageRatio(self, CPUAverageRatio):
        self.nodeLoad.set("CPUAverageRatio", CPUAverageRatio)
    def setCPULoadavg(self, CPULoadAvg):
	self.nodeLoad.set("CPULoadAvg", CPULoadAvg)

    def setCPUPeakRatio(self, CPUPeakRatio):
        self.nodeLoad.set("CPUPeakRatio", CPUPeakRatio)

    def setmemAverageRatio(self, memAverageRatio):
        self.nodeLoad.set("memAverageRatio", memAverageRatio)

    def setmemPeakRatio(self, memPeakRatio):
        self.nodeLoad.set("memPeakRatio", memPeakRatio)

    def setnorthboundIdleBW(self, northboundIdleBW):
        self.nodeLoad.set("northboundIdleBW", northboundIdleBW)

    def setnorthboundConcurrencies(self, northboundConcurrencies):
        self.nodeLoad.set("northboundConcurrencies", northboundConcurrencies)

    def setsouthboundIdleBW(self, southboundIdleBW):
        self.nodeLoad.set("southboundIdleBW", southboundIdleBW)

    def setsouthboundConcurriencies(self, southboundConcurriencies):
        self.nodeLoad.set("southboundConcurriencies", southboundConcurriencies)

    def setidleDiskSpace(self, idleDiskSpace):
        self.nodeLoad.set("idleDiskSpace", idleDiskSpace)

    def setDiskIOWBw(self, IOWBw):
        self.nodeLoad.set("IOWBw", IOWBw)

    def setDiskIORBw(self, IORBw):
        self.nodeLoad.set("IORBw", IORBw)

    def settimeStamp(self, timeStamp):
        self.nodeLoad.set("timeStamp", timeStamp)

    def setHostIP(self):
	self.nodeLoad.set("IP", self.ip)

    def setWeight(self,weight):
	self.nodeLoad.set("Weight",weight)

    def tostring(self):
        return ET.tostring(self.__root, encoding="UTF-8")
    
    def writeToFile(self):
        if self.filename is None:
            self.__logger.error("xml filename is null")
            print "xml filename is null"
            return

        try:
            self.__tree.write(os.path.join(self.wwwroot, self.filename), encoding="UTF-8")
        except Exception as exc:
            self.__logger.error("Exception: %s occured while write %s", exc, os.path.join(self.wwwroot, self.filename))
            print "Exception: %s occured while write %s"%(exc, os.path.join(self.wwwroot, self.filename))

    def postToServer(self):
        if self.posturl is None:
            self.__logger.error("posturl is null")
            print "posturl is null"
            return

        try:
            req = urllib2.Request(url=self.posturl, 
                                  data=self.tostring(), 
                                  headers={'Content-Type': 'application/xml'})
            urllib2.urlopen(req)
        except Exception as exc:
            self.__logger.error("Exception: %s occured post xml to: %s", exc, self.posturl)
            print "Exception: %s occured post xml to: %s"%(exc, self.posturl)


if __name__ == "__main__":
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    log_FileHandler = logging.handlers.TimedRotatingFileHandler(filename = "NodeStateXML.log",
                                                                when = 'D',
                                                                interval = 1,
                                                                backupCount = 7)
    
    log_FileHandler.setFormatter(formatter)
    log_FileHandler.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_FileHandler)


    ndst = NodeStateXML(filename="NodeState.xml", nodeID='jx_ja', wwwroot='/var/www')


    ndst.setNodeStatus("busy")
    ndst.writeToFile()
    print ndst.tostring()
