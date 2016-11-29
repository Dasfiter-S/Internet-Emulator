import sys
import time
import traceback
import SocketServer
import datetime
import time
import argparse
import threading
import Model
from dnslib import *

class Controller(object):

    def dns_response(self, data):
        request = DNSRecord.parse(data)
        print 'Searching: '
        print request
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        qn = request.q.qname
        strQuery = repr(qn)                            #remove class formatting
        strQuery = strQuery[12:-2]                     #DNSLabel type, strip class and take out string 

    #Will be able to specify files via terminal launch 
        temp = Model.IOitems()
        domainList = temp.loadFile('dnsCache.txt')
        domainDict = dict(domainList)
        blackList = temp.loadFile('blackList.txt')
        blackDictionary = dict(blackList)
        #self.printTest(threading.currentThread(), threading.enumerate())
        if blackDictionary.get(strQuery):              #have to implement view update
            reply.add_answer(RR(rname=qn, rtype=1, rclass=1, ttl=300, rdata=A(blackDictionary[strQuery])))
        else:
            if domainDict.get(strQuery):
                reply.add_answer(RR(rname=qn, rtype=1, rclass=1, ttl=300, rdata=A(domainDict[strQuery])))
            else:
                try:
                    if 1:#socket.inet_aton(socket.gethostbyname(strQuery)):
                        #responseIP = socket.gethostbyname(strQuery)             #only supports IPV4 can easily upgrade to IPV6
                        realDNS = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
                        realDNS.sendto(data,('8.8.8.8', 53))
                        exData, fromaddr = realDNS.recvfrom(1024)
                        realDNS.close()
                        exreq = DNSRecord.parse(exData) 
                        print '--------- Reply:\n', exreq
                        return exData 
                        #reply.add_answer(RR(rname=qn, rtype=1, rclass=1, ttl=300, rdata=A(responseIP)))
                except socket.gaierror: 
                    print 'Not a valid address'
 
        print '--------- Reply:\n', reply
        return reply.pack()   # replies with an empty pack if address is blocked or not found


    def printTest(self, currentThread, tnum):
        print 'Current thread: ' + str(currentThread)
        print 'Current threads alive: ' + str(tnum)


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
                self.send_data(Controller().dns_response(data))
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


    def launchOptions(self):
        parser = argparse.ArgumentParser(description='This program forwards DNS requests not found in the whitelist or blacklist')
        parser.add_argument('-p', '--port', help='select the port the DNS server runs on. Default port 53', type=int)

        arg = parser.parse_args()
        #set_DNSport(arg.dport)
        #set_wFile(arg.wfile)
        #set_bFile(arg.bfile)
        #set_HTTPport(arg.hport)
