#from Lumpy import Lumpy                                                    #UML generation code
import datetime
import sys
import time
import threading
import traceback
import SocketServer
from dnslib import *

#to do
#re-write DNS resolver
#re-write database
#add parameters to specify commandline files 
#for black list and white list 

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

def addToBlacklist(siteName, currentFile = 'blackList.txt'):
    with open(currentFile, 'r+') as domains:
        domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
        dictList = dict(domainList)
    with open(currentFile, 'a+') as fileData:
        if siteName in dictList:
            print siteName + ' already exists in database'
        elif sitename not in dictList:
            fileData.write(str(siteName) + ', ' + str(siteName) + '\n') 
         

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

        addToCache(self)

def dns_response(data):
    request = DNSRecord.parse(data)
    print 'Searching: ' 
    print request
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q) 

    qn = request.q.qname 
    strQuery = repr(qn)
    strQuery = strQuery[12:-2]                     #DNSLabel type, strip class and take out string 

    domainList = loadFile('dnsCache.txt')
    domainDict = dict(domainList)
    blackList = loadFile('blackList.txt')
    blackDictionary = dict(blackList)

    if blackDictionary.get(strQuery):
        print '________________________________________________________________________'
        print 'This site has been blocked. Contact your local admin for more information'
        print '________________________________________________________________________'
    else:
        if domainDict.get(strQuery):                     
            reply.add_answer(RR(rname=qn, rtype=1, rclass=1, ttl=300, rdata=A(domainDict[strQuery])))
        else:
            responseIP = socket.gethostbyname(strQuery)
            reply.add_answer(RR(rname=qn, rtype=1, rclass=1, ttl=300, rdata=A(responseIP)))
        
    print '--------- Reply:\n', reply
    return reply.pack()


class BaseRequestHandler(SocketServer.BaseRequestHandler):
    
    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print '\n\n%s request %s (%s %s):' % (self.__class__.__name__[:3], now, self.client_address[0], self.client_address[1])

        try:
            data = self.get_data()
            print len(data), data.encode('hex')
            self.send_data(dns_response(data))
        except Exception:
            traceback.print_exc(file=sys.stderr)


class TCPRequestHandler(BaseRequestHandler):
        
    def get_data(self):
        data = self.request.recv(8192)
        sz = int(data[:2].encode('hex'), 16)
        if sz < len(data) - 2:
            raise Exception('Wrong size of TCP packet')
        elif sz > len(data) - 2:
            raise Exception('Too big TCP packet')
        return data[2:]

    def send_data(self, data):
        sz  = hex(len(data))[2:].zfill(4).decode('hex')
        return self.request.sendall(sz + data)

class UDPRequestHandler(BaseRequestHandler, ):
    
    def get_data(self):
        return self.request[0]

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)
       
if __name__ == '__main__':
    print 'Starting DNS server! '
    #lumpy = Lumpy()                                                          #UML generation code
    #lumpy.make_reference()                                                   #UML generation code
    #myDomain = DomainItem('cnn.com', '127.0.0.20', 300, 8000, 'test')
    servers = [SocketServer.ThreadingUDPServer(('', 8000), UDPRequestHandler), 
               SocketServer.ThreadingTCPServer(('', 8000), TCPRequestHandler),
    ]
    for s in servers:
        thread = threading.Thread(target=s.serve_forever)
        thread.daemon = True
        thread.start()
        print '%s server loop running in thread: %s' % (s.RequestHandlerClass.__name__[:3], thread.name)
        #lumpy.object_diagram()                                                #UML generation code
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
