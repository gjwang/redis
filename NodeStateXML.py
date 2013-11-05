#!/usr/bin/python
import os
import socket
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
    def __init__(self, filename, nodeID, wwwroot = '/data', 
                 ip = None,
                 nodeStatus="idle", CntUserNow="200", CntUserMax="500", BWNow="200", BWMax="500", 
                 CPUAverageRatio="3", CPUPeakRatio="5", memAverageRatio="20", memPeakRatio="30", 
                 northboundIdleBW="100", northboundConcurrencies="150", southboundIdleBW="300", southboundConcurriencies="200",
                 idleDiskSpace="5t", IOWBw="50Mbps", IORBw="70Mbps", timeStamp="1383593423",                  
                 ifname='eth0', port = '8088', hostname = None, xmlUrl=None, 
                 ):

        self.__logger = logging.getLogger(self.__class__.__name__)
        
        self.filename = filename
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
        self.nodeLoad.set("CntUserNow", CntUserNow)
        self.nodeLoad.set("CntUserMax", CntUserMax)
        self.nodeLoad.set("BWNow", BWNow)
        self.nodeLoad.set("BWMax", BWMax)
        self.nodeLoad.set("CPUAverageRatio", CPUAverageRatio)
        self.nodeLoad.set("CPUPeakRatio", CPUPeakRatio)
        self.nodeLoad.set("memAverageRatio", memAverageRatio)
        self.nodeLoad.set("memPeakRatio", memPeakRatio)
        self.nodeLoad.set("northboundIdleBW", northboundIdleBW)
        self.nodeLoad.set("northboundConcurrencies", northboundConcurrencies)
        self.nodeLoad.set("southboundIdleBW", southboundIdleBW)
        self.nodeLoad.set("southboundConcurriencies", southboundConcurriencies)
        self.nodeLoad.set("idleDiskSpace", idleDiskSpace)
        self.nodeLoad.set("IOWBw", IOWBw)
        self.nodeLoad.set("IORBw", IORBw)
        self.nodeLoad.set("timeStamp", timeStamp)
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

    def setCPUPeakRatio(self, CPUPeakRatio):
        self.nodeLoad.set("CPUPeakRatio", CPUPeakRatio)

    def setmemPeakRatio(self, memPeakRatio):
        self.nodeLoad.set("memAverageRatio", memAverageRatio)

    def setmemPeakRatio(self, memPeakRatio):
        self.nodeLoad.set("memPeakRatio", memPeakRatio)

    def setnorthboundIdleBW(self, northboundIdleBW):
        self.nodeLoad.set("northboundIdleBW", northboundIdleBW)

    def setnorthboundIdleBW(self, northboundIdleBW):
        self.nodeLoad.set("northboundIdleBW", northboundConcurrencies)

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

    
    def writeToFile(self):
        try:
            self.__tree.write(os.path.join(self.wwwroot, self.filename), encoding="UTF-8", xml_declaration=True)
        except Exception as exc:
            self.__logger.error("Exception: %s occured while write %s", exc, os.path.join(self.wwwroot, self.filename))
            #print exc

    def tostring(self):
        return ET.tostring(self.__root, encoding="UTF-8")


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
