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
import logging
import sockDev
from dnslib import *


class IOitems(object):
    def __init__(self, port=None, hport=None, hsport=None, whiteFile=None, blackFile=None, saveOP=False):
        self.port = port
        self.http_port = hport
        self.https_port = hsport
        self.whitelist = whiteFile
        self.blacklist = blackFile
        self.save = saveOP


    def setPorts(self):
        if self.saveOp == False and (self.http_port is not None or self.https_port is not None):
             return
        else:
            temp = IOitems()
            items = temp.loadConfig()
            self.port = items['DNSport']
            self.http_port = items['HTTPport']
            self.https_port = items['HTTPSport']

    def loadFile(self, currentFile):
        try:
            with open(currentFile) as domains:
                domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
            return domainList
        except IOError:
            print 'File not found, specify a valid file'
            logging.error('File not found, please specify a valid file')
            sys.exit(1)

    def addToCache(self, DomainItem, currentFile):
        try:
            if DomainItem is not None:
                with open(currentFile, 'r+') as domains:
                    domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
                    dictList = dict(domainList)
                with open(currentFile, 'a+') as fileData:
                    if DomainItem.name in dictList:
                        print '%s already exists in database' % (DomainItem.name)
                        logging.debug('%s already exists in database' % (Domain.Item.name))
                    elif DomainItem.name not in dictList:
                        fileData.write('%s, %d \n' % (DomainItem.name, DomainItem.IP))
                        print '%s with IP %s has been added to the database' % (DomainItem.name, DomainItem.IP)
                        logging.debug('%s already exists in database' % (DomainItem.name))
        except IOError:
            print 'File not found, specify a valid file'
            logging.error('File not found, please specify a valid file')
            sys.exit(1)

    def addToBlacklist(self, siteName, IP,  currentFile):
        try:
            if IP is not None and siteName is not None:
                with open(currentFile, 'r+') as domains:
                    domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
                    dictList = dict(domainList)
                with open(currentFile, 'a+') as fileData:
                    if siteName in dictList:
                        print '%s already exists in database' % (sitename)
                        logging.debug('%s already exists in the database' % (sitename))
                    elif sitename not in dictList:
                        fileData.write('%s, %d \n' % (siteName, IP))
        except IOError:
            print 'File not found, specify a valid file'
            logging.debug('%s already exists in database' % (sitename))
            sys.exit(1)
    
    def loadConfig(self, currentFile='config.ini'):
        try:
            readfile = ConfigParser.ConfigParser()
            readfile.read(currentFile)
            serverConfig = {}
            if not readfile.has_section('Run_Time'):
                print 'File missing Run_Time section'
                logging.debug('File missing Run_Time section')
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
                logging.debug('File missing Domain section')
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
            print 'File not found, please specify a valid file'
            logging.debug('File not found, please specify a valid file')
            sys.exit(1)

    def writeToConfig(self, currentFile=None, DNSport=None, whiteFile=None, blackFile=None, http_port=None, https_port=None, vs_ports=None, certs=None, keys=None, handlers=None, name=None, domain=None):
        try:
           config_file = ConfigParser.ConfigParser()
           config_file.read(currentFile)
           if config_file.has_section('Run_Time'):
               print 'Adding items'
               logging.debug('Adding items')
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
               logging.debug('Adding section and items')
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
           print 'Writing to file: %s' % (currentFile)
           logging.debug('Writing to file: %s' % (currentFile))
           with open(currentFile, 'w') as configfile:
               config_file.write(configfile)
        except IOError:
            print 'File not found, specify a valid file'
            logging.debug('File not found, please specify a valid file')
            sys.exit(1)

    def set_DNSport(self, port):
        if port is not None:
            self.port = port

    def set_HTTPport(self, port):
        if port is not None:
            self.http_port = port

    def set_HTTPSport(self, port):
        self.https_port = port
        
    def set_save(self, save=None):
        if save is not None:
            self.saveOp = save

    def set_wFile(self, inFile):
        if inFile is not None:
             self.whitelist = inFile
             print 'WFin: %s' % inFile

    def set_bFile(self, inFile):
        if inFile is not None:
             self.blacklist = inFile
             print 'BFin: %s' % inFile

    def availablePorts(self, free_ports, servers=None):
        if len(free_ports) == 0:
            servers += 8000
            return servers
        else:
            return Model.HTTPShandler.port[0] 

    def addFreePorts(self, free_ports, free_port=None):
        free_ports.append(free_port)

    def make_VS(self, server_list, server_total, port, serverRequest, permissions):
        tool = Util.Util() 
        handler = Model.HandlerFactory()
        server_list.append('VS%d' % (server_total))
        server_list[server_total] = Model.VS_host(port, tool.get_path(permissions[0]),
                             tool.get_path(permissions[1]), handler.factory(serverRequest),
                             server_list[server_total])
        server_list[server_total].daemon = True
        server_list[server_total].start()
        handler.set_port(port)

    def startServers(self):
        #Port for either services will be set at launch on terminal or config file
        # run the DNS services
        
        #Initialize and run DNS, HTTP and HTTPS
        self.setPorts()
        serverList = Model.Server()
        DNS_server = serverList.factory('DNS', int(self.port))
        DNS_server.daemon = True
        DNS_server.start()

        test = sockDev.TestServer(int(self.https_port))
        test.daemon = True
        test.start()

#        http_server = serverList.factory('HTTP', self.http_port)
#        http_server.daemon = True
#        http_server.start()
        
        
        #initialize and run HTTPS services
#        https_server = serverList.factory('HTTPS', self.https_port)
#        https_server.daemon = True
#        https_server.start()

#        SNI_server = serverList.factory('SNI', self.https_port)
#        SNI_server.daemon = True
#        SNI_server.start()
        
        #Move these items to the config file
        certs = [#'/ubuntu1404/./server.key',
                 '/certs/./www.cnn.com.cert',
                 '/certs/./www.foo.com.cert',
                 '/certs/./test3cert.pem']

        keys = [# '/ubuntu1404/./server.crt',
                 '/certs/./www.cnn.com.key',
                 '/certs/./www.foo.com.key',
                 '/certs/./test3key.pem']

        permissions = [certs[0], keys[0]]
        logging.debug('Permissions \n Cert: %s \n Key: %s ' % (permissions[0], permissions[1]))

        serverNames = ['nginx', 'IIS', 'Apache', 'gws', 'lighttpd'] #This list will be replaced by header requests
#        sites_up[hostname] = server_name
#        self.make_VS(virtual_servers, 0, self.availablePorts(free_ports, 0), serverNames[3], permissions)
#        test = serverList.factory('TestHTTPS', 8000)
#        test.daemon = True
#        test.start()
        #create method for get_cert that matches host request
         
        #Test
#        sites = Model.HTTPShandler.pathways['cnn.com']
#        print 'Sites: ', sites
#        sites = sites[:-1] + '9'
#        print 'Sites: ', sites
       

class Controller(IOitems):

    #Receives the raw DNS query data and extracts the name of the address. Checks the address agaisnt specified
    #lists. If the address is not found then it is forwarded to an external DNS to resolve. Forwarded
    #requests send the raw query data and receive raw data.
    def dns_response(self, data):
        request = DNSRecord.parse(data)
#        print 'Searching: \n %s' % (str(request))
        logging.debug('Searching: \n %s' % (str(request)))
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        query_name = request.q.qname                     #is preserved so that we can reply with proper formatting later
        str_query = repr(query_name)                     #remove class formatting
        str_query = str_query[12:-2]                     #DNSLabel type, strip class and take out string  

        list_names = Model.setLists(self)
        domainList = self.loadFile(list_names[0])
        domainDict = dict(domainList)
        blackList = self.loadFile(list_names[1])
        blackDictionary = dict(blackList)
        address = urlparse.urlparse(str_query)
        if blackDictionary.get(str_query):             
            reply.add_answer(RR(rname=query_name, rtype=1, rclass=1, ttl=300, rdata=A('127.0.0.1')))
        else:
            if domainDict.get(str_query):
                reply.add_answer(RR(rname=query_name, rtype=1, rclass=1, ttl=300, rdata=A(domainDict[str_query])))
            else:
                try:
                    realDNS = socket.socket( socket.AF_INET, socket.SOCK_DGRAM)
                    realDNS.sendto(data,('8.8.8.8', 53))
                    answerData, fromaddr = realDNS.recvfrom(1024)
                    realDNS.close()
                    readableAnswer = DNSRecord.parse(answerData) 
#                    print'--------- Reply:\n %s' % (str(readableAnswer))
                    logging.debug('DNS Reply: \n %s' % (str(readableAnswer)))
                    return answerData 
                except socket.gaierror: 
                    print '-------------NOT A VALID ADDRESS--------------'
                    logging.error('Not a valid address %s' % (str_query))
 
#        print '--------- Reply:\n %s' % (str(reply))
        logging.debug('DNS Reply: \n %s' % (str(reply)))
        return reply.pack()   # replies with an empty pack if address is not found
    

    def printThreads(self, currentThread, tnum):
        print 'Current thread: %s \n Current threads alive: %d' % (str(currentThread), tnum)
        logging.debug('Current thread: %s \n Current threads alive: %d' % (str(currentThread), tnum))


    class BaseRequestHandler(SocketServer.BaseRequestHandler):

        def get_data(self):
            raise NotImplementedError

        def send_data(self, data):
            raise NotImplementedError

        def handle(self):
            now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
#            print '\n\n%s request %s (%s %s):' % (self.__class__.__name__[:3], now, self.client_address[0], self.client_address[1])
            logging.debug('\n\n%s request %s (%s %s):' % (self.__class__.__name__[:3], now, self.client_address[0], self.client_address[1]))
            
            try:
                data = self.get_data()
                print len(data), data.encode('hex')
                logging.debug('Length: %d %s' % (len(data), data.encode('hex')))
                self.send_data(Controller().dns_response(data))
            except Exception:
                traceback.print_exc(file=sys.stderr)

    class UDPRequestHandler(BaseRequestHandler, ):

        def get_data(self):
            return self.request[0]

        def send_data(self, data):
            return self.request[1].sendto(data, self.client_address)
 
