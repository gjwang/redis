#!/usr/bin/env python

'''
Created on 2013-11-04

@author: gjwang
'''

"""
List the Node's state
"""

import sys
import os
import time
import logging
import logging.handlers

import psutil
from psutil._compat import print_

import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM

AD = "-"
AF_INET6 = getattr(socket, 'AF_INET6', object())
proto_map = {(AF_INET, SOCK_STREAM)  : 'tcp',
             (AF_INET6, SOCK_STREAM) : 'tcp6',
             (AF_INET, SOCK_DGRAM)   : 'udp',
             (AF_INET6, SOCK_DGRAM)  : 'udp6'}


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n



class NodeState(object):
    def __init__(self, interval = 10, mountpoint='/data', device = None, netcard = 'eth0', psname = None):
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.interval = interval
        self.mountpoint = mountpoint
        self.device = device
        self.netcard = netcard
        self.psname = psname

        self.disks_read = 0 
        self.disks_write = 0
        self.netsent = 0
        self.recv = 0
        self.cpuuaage = 0

    def get_diskfree(self):
        #templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
        #print_(templ % ("Device", "Total", "Used", "Free", "Use ", "Type", "Mount"))

        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    # skip cd-rom drives with no disk in it; they may raise
                    # ENOENT, pop-up a Windows GUI error for a non-ready
                    # partition or just hang.
                    continue

            if part.mountpoint == self.mountpoint or part.device == self.device:
                usage = psutil.disk_usage(part.mountpoint)
                #print "freedisk %s" % usage.free                
                #print_(templ % (part.device,
                #            bytes2human(usage.total),
                #            bytes2human(usage.used),
                #            bytes2human(usage.free),
                #            int(usage.percent),
                #            part.fstype,
                #            part.mountpoint))
                return usage.free
            else:
                #usage = psutil.disk_usage(part.mountpoint)
                continue

        return 0
            

    def set_interval(self, interval):
        self.interval = interval

    def get_memusage(self):
        return psutil.virtual_memory().percent
    
    def get_cpuusage(self):
        # cpu usage
        #for cpu_num, perc in enumerate(psutil.cpu_percent(interval=0, percpu=True)):
        #print "cpu_num:%s, perc:%s" % (cpu_num, perc)
        #return psutil.cpu_percent(interval=0)
        return self.cpuuaage




    #psname: process name
    #psname is None, return the total tcp connections
    #return the psname's tcp connections
    def get_connections(self):
        #templ = "%-5s %-22s %-22s %-13s %-6s %s"
        #print_(templ % ("Proto", "Local addr", "Remote addr", "Status", "PID",
        #                "Program name"))

        conn_type = 'tcp'
        tcp_conns = 0
        #udp_conns = 0

        for p in psutil.process_iter():
            name = '?'
            try:
                name = p.name
                if self.psname is not None and self.psname != name:
                    continue

                cons = p.get_connections(kind='inet')
            except psutil.AccessDenied:
                #print_(templ % (AD, AD, AD, AD, p.pid, name))
                pass
            except psutil.NoSuchProcess:
                continue
            else:
                for c in cons:
                    if conn_type == proto_map[(c.family, c.type)] and c.status == 'ESTABLISHED':
                        tcp_conns = tcp_conns + 1

        #print "psname: %s, tcpconns: %s" % (self.psname, tcp_conns)
        return tcp_conns
 

    def get_io(self):        
        def refresh_netinfo(tot_before, tot_after, pnic_before, pnic_after):        
            if self.netcard is None:
                # totals
                #templ = "%-15s %15s %15s"
                #print_(templ % ("TYPE", "TOTAL", "PER-SEC"))
                #print_(templ % (
                #        "bytes-sent",
                #        bytes2human(tot_after.bytes_sent),
                #        bytes2human(tot_after.bytes_sent - tot_before.bytes_sent) + '/s',
                #      ))
                #print_(templ % (
                #        "bytes-recv",
                #        bytes2human(tot_after.bytes_recv),
                #        bytes2human(tot_after.bytes_recv - tot_before.bytes_recv) + '/s',
                #        ))        
                return tot_after.bytes_sent - tot_before.bytes_sent, tot_after.bytes_recv - tot_before.bytes_recv
                
            # per-network interface details: let's sort network interfaces so
            # that the ones which generated more traffic are shown first
            #print_("")
            nic_names = list(pnic_after.keys())
            nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
            for name in nic_names:
                if name != self.netcard:
                    continue
                stats_before = pnic_before[name]
                stats_after = pnic_after[name]
                #templ = "%-15s %15s %15s"
                #print_(templ % (name, "TOTAL", "PER-SEC"))
                #print_(templ % (
                #        "bytes-sent",
                #        bytes2human(stats_after.bytes_sent),
                #        bytes2human(stats_after.bytes_sent - stats_before.bytes_sent) + '/s',
                #        ))
                #print_(templ % (
                #        "bytes-recv",
                #        bytes2human(stats_after.bytes_recv),
                #        bytes2human(stats_after.bytes_recv - stats_before.bytes_recv) + '/s',
                #        ))
                #print_(templ % (
                #    "pkts-sent",
                #    stats_after.packets_sent,
                #    stats_after.packets_sent - stats_before.packets_sent,
                #))
                #print_(templ % (
                #    "pkts-recv",
                #    stats_after.packets_recv,
                #    stats_after.packets_recv - stats_before.packets_recv,
                #))
                #print_("")

                return stats_after.bytes_sent - stats_before.bytes_sent, stats_after.bytes_recv - stats_before.bytes_recv
            return 0, 0

        disks_before = psutil.disk_io_counters()
        tot_before = psutil.net_io_counters()
        pnic_before = psutil.net_io_counters(pernic=True)

        # sleep some time
        #TODO: psutil.cpu_percent(interval=self.interval)
        #time.sleep(self.interval)
        psutil.cpu_percent(interval=self.interval)

        disks_after = psutil.disk_io_counters()
        tot_after = psutil.net_io_counters()
        pnic_after = psutil.net_io_counters(pernic=True)


        self.disks_read = disks_after.read_bytes - disks_before.read_bytes
        self.disks_write = disks_after.write_bytes - disks_before.write_bytes

        self.netsent, self.netrecv = refresh_netinfo(tot_before, tot_after, pnic_before, pnic_after)

        #print "dk r:%sb/s, w:%sb/s" % (disks_read_per_sec, disks_write_per_sec)
        return (self.disks_read, self.disks_write, self.netsent, self.netrecv)



interval = 5
mountpoint = '/home'
device = None #device='/dev/sda9'
netcard = 'eth0'
psname = 'chrome'


if __name__ == '__main__':
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


    ndst = NodeState(interval=interval, mountpoint=mountpoint, device=device, netcard=netcard, psname=psname)

    try:
        while 1:
            print "diskfree: %s" % ndst.get_diskfree()
            print "memusage: %s" % ndst.get_memusage()
            print "dkr:%s, dkw:%s, nets:%s, netr:%s" % ndst.get_io()
            
            #get_cpuusage must after get_io
            print "cpuusage: %s" % ndst.get_cpuusage()
            print "conns:    %s" % ndst.get_connections()
            ndst.set_interval(interval)
    except Exception as exc:
        print exc


