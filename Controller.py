import sys
import time
import traceback
import SocketServer
import datetime
import time
import threading
import Model
import View
import urlparse
from dnslib import *


class Controller(Model.IOitems):
    #Receives the raw DNS query data and extracts the name of the address. Checks the address agaisnt specified
    #lists. If the address is not found then it is forwarded to an external DNS to resolve. Forwarded
    #requests send the raw query data and receive raw data.
    def dns_response(self, data):
        log = View.View()
        request = DNSRecord.parse(data)
        print 'Searching: '
        print request
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        qn = request.q.qname
        strQuery = repr(qn)                            #remove class formatting
        strQuery = strQuery[12:-2]                     #DNSLabel type, strip class and take out string  

        temp = Model.RunTimeItems(self.whitelist, self.blacklist, self.saveOp)
        temp.setLists()
        domainList = self.loadFile(temp.whitelist)
        domainDict = dict(domainList)
        blackList = self.loadFile(temp.blacklist)
        blackDictionary = dict(blackList)
        address = urlparse.urlparse(strQuery)
        if blackDictionary.get(strQuery):             
            reply.add_answer(RR(rname=qn, rtype=1, rclass=1, ttl=300, rdata=A('127.0.0.1')))
        else:
            if domainDict.get(strQuery):
                reply.add_answer(RR(rname=qn, rtype=1, rclass=1, ttl=300, rdata=A(domainDict[strQuery])))
            else:
                try:
                    realDNS = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
                    realDNS.sendto(data,('8.8.8.8', 53))
                    answerData, fromaddr = realDNS.recvfrom(1024)
                    realDNS.close()
                    readableAnswer = DNSRecord.parse(answerData) 
                    print'--------- Reply:\n'
                    print str(readableAnswer)
                    return answerData 
                except socket.gaierror: 
                    print '-------------NOT A VALID ADDRESS--------------'
 
        print '--------- Reply:\n'
        print reply
        return reply.pack()   # replies with an empty pack if address is not found
    

    def printThreads(self, currentThread, tnum):
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

    class UDPRequestHandler(BaseRequestHandler, ):

        def get_data(self):
            return self.request[0]

        def send_data(self, data):
            return self.request[1].sendto(data, self.client_address)

