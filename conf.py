# -*- coding: utf-8 -*- 

'''
Created on 2013年10月29日

@author: gjwang
'''
#region's name for short for nodeID
nodeID = 'jx_ja'
#post interval
interval = 10
#mountpoint for main disk
mountpoint = '/data'
device = None #device='/dev/sda9'
netcard = 'eth0'
#port for nginx in local host
port = '80'
#publishing server's name
psname = 'ngnix'
#the host's url for posting xml file
postUrl = 'http://xxx:port/lua'
#
wwwroot = '/data/ysten'
#xml file for posting
xmlfilename="NodeState.xml"
#program's log 
logfilename = "log/nodestate.log"
#所有主机整体配置的综合系数
weight=1
