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
import Util
import ConfigParser
from dnslib import *


class Controller(object):
    def __init__(self, whitefile=None, blackfile=None)
        self.whitelist = whitefile
        self.blacklist = blackfile
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
 

class IOitems(object):
    def __init__(self, port=53, hport=None, hsport=None):
        self.port = port
        self.http_port = hport
        self.https_port = hsport


    def setPorts(self):
        if self.saveOp == False and (self.http_port is not None or self.https_port is not None):
             return
        else:
            temp = IOitems()
            items = temp.loadConfig()
            self.http_port = items['HTTPport']
            self.https_port = items['HTTPSport']

    def loadFile(self, currentFile):
        try:
            with open(currentFile) as domains:
                domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
            return domainList
        except IOError:
            print 'File not found, specify a valid file'
            sys.exit(1)

    def addToCache(self, DomainItem, currentFile):
        try:
            if DomainItem is not None:
                with open(currentFile, 'r+') as domains:
                    domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
                    dictList = dict(domainList)
                with open(currentFile, 'a+') as fileData:
                    if DomainItem.name in dictList:
                        print DomainItem.name + ' already exists in database'
                    elif DomainItem.name not in dictList:
                        fileData.write(str(DomainItem.name) + ', ' + str(DomainItem.IP) + '\n')
                        print DomainItem.name + ' with IP ' + DomainItem.IP + ' has been added to the database'
        except IOError:
            print 'File not found, specify a valid file'
            sys.exit(1)

    def addToBlacklist(self, siteName, IP,  currentFile):
        try:
            if IP is not None and siteName is not None:
                with open(currentFile, 'r+') as domains:
                    domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
                    dictList = dict(domainList)
                with open(currentFile, 'a+') as fileData:
                    if siteName in dictList:
                        print siteName + ' already exists in database'
                    elif sitename not in dictList:
                        fileData.write(str(siteName) + ', ' + str(IP) + '\n')
        except IOError:
            print 'File not found, specify a valid file'
            sys.exit(1)
    
    def loadConfig(self, currentFile='config.ini'):
        try:
            readfile = ConfigParser.ConfigParser()
            readfile.read(currentFile)
            serverConfig = {}
            if not readfile.has_section('Run_Time'):
                print 'File missing Run_Time section'
            elif readfile.has_section('Run_Time'):
                if readfile.has_option('Run_Time', 'DNSport'):
                    serverConfig['DNSport'] = readfile.get('Run_Time', 'DNSport')
                if readfile.has_option('Run_Time', 'Whitelist'):
                    serverConfig['Whitelist'] = readfile.get('Run_Time', 'Whitelist')
                if readfile.has_option('Run_Time', 'Blacklist'):
                    serverConfig['Blacklist'] = readfile.get('Run_Time', 'Blacklist')
                if readfile.has_option('Run_Time', 'HTTPport'):
                    serverConfig['HTTPport'] = readfile.get('Run_Time', 'HTTPport') 
                if readfile.has_option('Run_Time', 'HTTPSport'):
                    serverConfig['HTTPSport'] = readfile.get('Run_Time', 'HTTPSport')
                if readfile.has_option('Run_Time', 'VS_Ports'):
                    serverConfig['VS_Ports'] = readfile.get('Run_Time', 'VS_Ports')
                if readfile.has_option('Run_Time', 'Certs'):
                    serverConfig['Certs'] = readfile.get('Run_Time', 'Certs')
                if readfile.has_option('Run_Time', 'Keys'):
                    serverConfig['Keys'] = readfile.get('Run_Time', 'Keys')
                if readfile.has_option('Run_Time', 'Handlers'):
                    serverConfig['Handlers'] = readfile.get('Run_Time', 'Handlers') 
                if readfile.has_option('Run_Time', 'Name'):
                    serverConfig['Name'] = readfile.get('Run_Time', 'Name')
            if not readfile.has_section('Domain'):
                print 'File missing Domain section'
            elif readfile.has_section('Domain'):
                #load the params
                if readfile.has_option('Run_Time', 'SiteName'):
                    serverConfig['SiteName'] = readfile.get('Domain', 'SiteName')
                if readfile.has_option('Run_Time', 'IP'):
                    serverConfig['IP'] = readfile.get('Domain', 'IP')
                if readfile.has_option('Run_Time', 'TTL'):    
                    serverConfig['TTL'] = readfile.get('Domain', 'TTL')
                if readfile.has_option('Run_Time', 'Port'):    
                    serverConfig['Port'] = readfile.get('Domain', 'Port')
                if readfile.has_option('Run_Time', 'Admin'):
                    serverConfig['Admin'] = readfile.get('Domain', 'Admin')
            return serverConfig
        except IOError:
            print 'File not found, specify a valid file'
            sys.exit(1)

    def writeToConfig(self, currentFile=None, DNSport=None, whiteFile=None, blackFile=None, http_port=None, https_port=None, vs_ports=None, certs=None, keys=None, handlers=None, name=None, domain=None):
        try:
           config_file = ConfigParser.ConfigParser()
           config_file.read(currentFile)
           if config_file.has_section('Run_Time'):
               print 'Adding items'
               if DNSport is not None:
                   config_file.set('Run_Time', 'DNSport', DNSport)
               if whiteFile is not None:
                   config_file.set('Run_Time', 'Whitelist', whiteFile)
               if blackFile is not None:
                   config_file.set('Run_Time', 'Blacklist', blackFile)
               if http_port is not None:
                   config_file.set('Run_Time', 'HTTPport', http_port)
               if https_port is not None:
                   config_file.set('Run_Time', 'HTTPSport', https_port)
               #Virtual server configs 
               if https_port is not None:
                   config_file.set('Run_Time', 'VS_Ports', vs_ports)
               if https_port is not None:
                   config_file.set('Run_Time', 'Certs', certs)
               if https_port is not None:
                   config_file.set('Run_Time', 'Keys', keys)
               if https_port is not None:
                   config_file.set('Run_Time', 'Handlers', handlers)
               if https_port is not None:
                   config_file.set('Run_Time', 'Name', name)
           elif not config_file.has_section('Run_Time'):
               #create config section
               print 'Adding section and items'
               config_file.add_section('Run_Time')
               if DNSport is not None:
                   config_file.set('Run_Time', 'DNSport', DNSport)
               else:
                   config_file.set('Run_Time', 'DNSport', '8000')
               if whiteFile is not None:
                   config_file.set('Run_Time', 'Whitelist', whiteFile)
               else:
                   config_file.set('Run_Time', 'Whitelist', 'DNSCache.txt')
               if blackFile is not None:
                   config_file.set('Run_Time', 'Blacklist', blackFile)
               else:
                   config_file.set('Run_Time', 'Blacklist', 'blackList.txt')
               if http_port is not None:
                   config_file.set('Run_Time', 'HTTPport', http_port)
               else:
                   config_file.set('Run_Time', 'HTTPport', '80')
               if https_port is not None:
                   config_file.set('Run_Time', 'HTTPSport', https_port)
               else:
                   config_file.set('Run_Time', 'HTTPSport', '443')
           if not config_file.has_section('Domain'):
               config_file.add_section('Domain')
               if domain is not None:
                   config_file.set('Domain', 'SiteName', domain.name)
                   config_file.set('Domain', 'IP', domain.IP)
                   config_file.set('Domain', 'TTL', domain.TTL)
                   config_file.set('Domain', 'Port', domain.port)
                   config_file.set('Domain', 'Admin', domain.admin)
           elif config_file.has_section('Domain'):
               if domain is not None:
                   config_file.set('Domain', 'SiteName', domain.name)
                   config_file.set('Domain', 'IP', domain.IP)
                   config_file.set('Domain', 'TTL', domain.TTL)
                   config_file.set('Domain', 'Port', domain.port)
                   config_file.set('Domain', 'Admin', domain.admin)
           print 'Writing to file: ' + currentFile
           with open(currentFile, 'w') as configfile:
               config_file.write(configfile)
        except IOError:
            print 'File not found, specify a valid file'
            sys.exit(1)

    def set_DNSport(self, port):
        if port is not None:
            self.port = port

    def get_DNSport(self):
        return self.port

    def set_HTTPport(self, port):
        if port is not None:
            self.http_port = port

    def get_HTTPport(self):
        return self.http_port

    def set_HTTPSport(self, port):
        self.https_port = port
        
    def set_save(self, save=None):
        if save is not None:
            self.saveOp = save

    def get_save(self):
        return self.saveOp

    def set_wFile(self, inFile):
        if inFile is not None:
             whitelist = inFile
             print 'WFin: ', inFile

    def get_wFile(self):
        return whitelist

    def set_bFile(self, inFile):
        if inFile is not None:
             blacklist = inFile
             print 'BFin: ', inFile

    def get_bFile(self):
        return self.blacklist

    def startServers(self):
        #Port for either services will be set at launch on terminal or config file
        # run the DNS services
        tool = Util.Util()
        server = [SocketServer.ThreadingUDPServer(('', self.port), Controller.UDPRequestHandler),]
        thread = threading.Thread(target=server[0].serve_forever)
        thread.daemon = True
        thread.start()
        print 'UDP server loop running on port ' + str(self.port) #in thread: %s % (thread.name)

        #Initialize and run HTTP services
        self.setPorts()
        serverList = Model.Server()

        http_server = serverList.factory('HTTP', self.http_port)
        http_server.daemon = True
        http_server.start()

        #initialize and run HTTPS services
        https_server = serverList.factory('HTTPS', self.https_port)
        https_server.daemon = True
        https_server.start()
        
        #Move these items to the config file
        certs = [#'/Users/ricardocarretero/dev/vm/ubuntu1404/./server.key',
                 '/certs/./test1cert.pem',
                 '/certs/./test2cert.pem',
                 '/certs/./test3cert.pem']

        keys = [# '/Users/ricardocarretero/dev/vm/ubuntu1404/./server.crt',
                 '/certs/./test1key.pem',
                 '/certs/./test2key.pem',
                 '/certs/./test3key.pem']
        ports = [#443, 
                 8000, 8001, 8002]
        VS_servers = []
        serverNames = ['nginx', 'IIS', 'Apache', 'gws', 'lighttpd']
        URLs = ['', '/test-pages/test2', '/test-pages/test3']
        for number in range(len(keys)):
            VS_servers.append('VS' + str(number))
            VS_servers[number] = Model.VS_host(ports[number], tool.get_path(certs[number]), tool.get_path(keys[number]), Model.VirtualHandler(serverNames[number], URLs[number]), name= VS_servers[number])
            VS_servers[number].daemon = True
            VS_servers[number].start()

        try:        #move to main or controller and re-write
            while 1:
                time.sleep(1)
                sys.stderr.flush()
                sys.stdout.flush()

        except KeyboardInterrupt:
            pass
        finally:
               server[0].shutdown()
               print 'Server terminated by SIGINT'

