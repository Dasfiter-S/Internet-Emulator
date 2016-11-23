import SocketServer
import threading
import sys
from Controller import *
from dnslib import *


class DomainItem():

    def __init__(self, inName = 'thistest.com', inIP = '127.0.0.100', inTTL = 300, inPort = 53, inAdmin = 'admin'):
        self.name = inName + '.'
        self.IP = inIP
        self.TTL = inTTL
        self.port = inPort                                     #default 53
        self.admin = inAdmin
        self.mname = '{1} {0}'.format(self.name, 'ns1.')
        self.rname = '{1} {0}'.format(self.name, self.admin + '.')
        self.mail =  '{1} {0}'.format(self.name, 'mail' + '.')
        self.refresh = 60 * 60 * 1
        self.expire = 60 * 60 * 24
        self.minimum = 60 * 60 * 1
        self.times = (201307231,  # serial number
        self.refresh,
        60 * 60 * 3,  # retry
        self.expire,
        self.minimum,
        )
        self.soa_record = SOA(self.mname, self.rname, self.times)
        self.ns_records = [NS(self.mname)]
        self.records = {self.name:[A(self.IP)] + self.ns_records,
        self.mname: [A(self.IP)], self.mail: [A(self.IP)], self.rname: [CNAME(self.name)],}


class IOitems(object):
    def loadFile(currentFile = 'dnsCache.txt'):
        with open(currentFile) as domains:
            domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
        return domainList

    def addToCache(DomainItem, currentFile = 'dnsCache.txt'):
        with open(currentFile, 'r+') as domains:
            domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
            dictList = dict(domainList)
        with open(currentFile, 'a+') as fileData:
            if DomainItem.name in dictList:
                print DomainItem.name + ' already exists in database'
            elif DomainItem.name not in dictList:
                fileData.write(str(DomainItem.name) + ', ' + str(DomainItem.IP) + '\n')
                print DomainItem.name + ' with IP ' + DomainItem.IP + ' has been added to the database'

    def addToBlacklist(siteName, IP='255.255.255.255',  currentFile = 'blackList.txt'):
        with open(currentFile, 'r+') as domains:
            domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
            dictList = dict(domainList)
        with open(currentFile, 'a+') as fileData:
            if siteName in dictList:
                print siteName + ' already exists in database'
            elif sitename not in dictList:
                fileData.write(str(siteName) + ', ' + str(IP) + '\n')

    def setPort(portIn):
        self.port = portIn
   
    def getPort():
        return self.port

    def startServer(self, controller):
        #Port will be set at launch on terminal
        servers = [SocketServer.ThreadingUDPServer(('', 53), controller.UDPRequestHandler),
                   #SocketServer.ThreadingTCPServer(('', 53), controller.TCPRequestHandler),
        ]
        #for s in servers:
        if 1:
            thread = threading.Thread(target=servers[0].serve_forever)
            thread.daemon = True
            thread.start()
            print '%s server loop running in thread: %s' % (s.RequestHandlerClass.__name__[:3], thread.name)
        try:
            while 1:
                time.sleep(1)
                sys.stderr.flush()
                sys.stdout.flush()

        except KeyboardInterrupt:
            pass
        finally:
            for s in servers:
                s.shutdown()

