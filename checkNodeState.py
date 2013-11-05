#!/usr/bin/env python

'''
Created on 2013-11-04

@author: gjwang
'''

"""
List the Node's state
List all mounted disk partitions a-la "df -h" command.
"""

import sys
import os
import time
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


def get_diskstate(interval, mountpoint =None, device = None):
    #templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
    #print_(templ % ("Device", "Total", "Used", "Free", "Use ", "Type", "Mount"))

    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue

        if part.mountpoint == mountpoint or part.device == device:
            usage = psutil.disk_usage(part.mountpoint)
            print "freedisk %s" % usage.free
            #print_(templ % (part.device,
            #            bytes2human(usage.total),
            #            bytes2human(usage.used),
            #            bytes2human(usage.free),
            #            int(usage.percent),
            #            part.fstype,
            #            part.mountpoint))
            break            
        else:
            #usage = psutil.disk_usage(part.mountpoint)
            continue

            

    #disks_before = psutil.disk_io_counters()
    #time.sleep(interval)
    #disks_after = psutil.disk_io_counters()

    #disks_read_per_sec = disks_after.read_bytes - disks_before.read_bytes
    #disks_write_per_sec = disks_after.write_bytes - disks_before.write_bytes

    #print "dk r:%sb/s, w:%sb/s" % (disks_read_per_sec, disks_write_per_sec)


def get_meminfo():
    meminfo = psutil.virtual_memory()
    print "mem use: %s%%" % meminfo.percent
    
def get_cpuinfo():
    # cpu usage
    #for cpu_num, perc in enumerate(psutil.cpu_percent(interval=0, percpu=True)):
        #print "cpu_num:%s, perc:%s" % (cpu_num, perc)

    print "cpu_percent: %s" % psutil.cpu_percent(interval=0)



#netcard is None: return the total net info, else return the special card net info
#return the send and receiv bytes/interval(seconds)
def get_netinfo(interval, netcard = None):
    """Retrieve raw stats within an interval window."""

    def refresh_netinfo(tot_before, tot_after, pnic_before, pnic_after):
        if netcard is None:
            # totals
            templ = "%-15s %15s %15s"
            print_(templ % ("TYPE", "TOTAL", "PER-SEC"))
            print_(templ % (
                "bytes-sent",
                bytes2human(tot_after.bytes_sent),
                bytes2human(tot_after.bytes_sent - tot_before.bytes_sent) + '/s',
            ))
            print_(templ % (
                "bytes-recv",
                bytes2human(tot_after.bytes_recv),
                bytes2human(tot_after.bytes_recv - tot_before.bytes_recv) + '/s',
            ))        
            return tot_after.bytes_sent - tot_before.bytes_sent, tot_after.bytes_recv - tot_before.bytes_recv
                
        # per-network interface details: let's sort network interfaces so
        # that the ones which generated more traffic are shown first
        print_("")
        nic_names = list(pnic_after.keys())
        nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
        for name in nic_names:
            if name != netcard:
                continue
            stats_before = pnic_before[name]
            stats_after = pnic_after[name]
            templ = "%-15s %15s %15s"
            print_(templ % (name, "TOTAL", "PER-SEC"))
            print_(templ % (
                "bytes-sent",
                bytes2human(stats_after.bytes_sent),
                bytes2human(stats_after.bytes_sent - stats_before.bytes_sent) + '/s',
            ))
            print_(templ % (
                "bytes-recv",
                bytes2human(stats_after.bytes_recv),
                bytes2human(stats_after.bytes_recv - stats_before.bytes_recv) + '/s',
            ))
            print_(templ % (
                "pkts-sent",
                stats_after.packets_sent,
                stats_after.packets_sent - stats_before.packets_sent,
            ))
            print_(templ % (
                "pkts-recv",
                stats_after.packets_recv,
                stats_after.packets_recv - stats_before.packets_recv,
            ))
            print_("")

            return stats_after.bytes_sent - stats_before.bytes_sent, stats_after.bytes_recv - stats_before.bytes_recv


    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)
    # sleep some time
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)

    return refresh_netinfo(tot_before, tot_after, pnic_before, pnic_after)

#psname: process name
#psname is None, return the total tcp connections
#return the psname's tcp connections
def get_connections(psname = None):
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
            if psname is not None and psname != name:
                continue

            cons = p.get_connections(kind='inet')
        except psutil.AccessDenied:
            #print_(templ % (AD, AD, AD, AD, p.pid, name))
            pass
        except psutil.NoSuchProcess:
            continue
        else:
            for c in cons:
                #raddr = ""
                #laddr = "%s:%s" % (c.laddr)
                #if c.raddr:
                #    raddr = "%s:%s" % (c.raddr)
                #print_(templ % (proto_map[(c.family, c.type)],
                #                laddr,
                #                raddr,
                #                c.status,
                #                p.pid,
                #                name[:15]))
                
                if conn_type == proto_map[(c.family, c.type)] and c.status == 'ESTABLISHED':
                    tcp_conns = tcp_conns + 1

    print "psname: %s, tcpconns: %s" % (psname, tcp_conns)
    return tcp_conns
 

interval = 1
mountpoint = '/home'
device = None #device='/dev/sda9'
netcard = 'eth0'
psname = 'chrome'

def main():
    get_diskstate(interval, mountpoint, device)
    get_meminfo()
    get_cpuinfo()
    get_netinfo(interval, netcard)
    get_connections(psname)

if __name__ == '__main__':
    sys.exit(main())
