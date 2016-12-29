import SocketServer
import threading
import Queue
import sys
import Controller
import os
import argparse
import ConfigParser
import SimpleHTTPServer
import BaseHTTPServer
import urllib
import posixpath
import shutil
import cgi
import ssl
from dnslib import *
from multiprocessing.dummy import Pool as ThreadPool


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

        #item = IOitems()
        #item.addToCache(self, controller.get_blacklist)

class Http_start(threading.Thread):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        try:
            print 'Serving HTTP at port', self.port
            http = SocketServer.TCPServer(('', int(self.port)), MyRequestHandler)
            http.serve_forever()
        except KeyboardInterrupt:
            http.server_close()

class Https_start(threading.Thread):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        try:
            print 'Serving HTTPS at port', self.port
            https = BaseHTTPServer.HTTPServer(('', int(self.port)), MyRequestHandler)
            https.socket = ssl.wrap_socket(https.socket, certfile='./server.crt', server_side=True, keyfile='server.key')
            https.serve_forever()
        except KeyboardInterrupt:
            https.close()

class VS_host(threading.Thread):
    def __init__(self, port=8000, cert=None, key=None, handler= None, name= ''):
        threading.Thread.__init__(self)
        self.port = port
        self.cert = cert
        self.key = key
        self.handler = handler
        self.name = name

    def run(self):
        try:
            if self.cert is not None:
                print 'HTTPS '+ self.name  + ' on port: ', self.port
                VS = BaseHTTPServer.HTTPServer(('', int(self.port)), self.handler)
                VS.socket = ssl.wrap_socket(VS.socket, certfile= self.cert, server_side=True, keyfile= self.key)
                VS.serve_forever()
            else:
                print 'HTTP '+ self.name  + ' on port: ', self.port
                VS = BaseHTTPServer.HTTPServer(('', int(self.port)), MyRequestHandler)
                VS.serve_forever()
        except KeyboardInterrupt:
            VS.close()


class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    server_version = 'nginx'
    sys_version = ''
    pathways = {'/test-pages': 'https://127.0.0.1/test-pages', 
                '/test-pages/': 'https://127.0.0.1/test-pages/',
                '/test-pages/test1': 'https://127.0.0.1:8000/test-pages/test1',
                '/test-pages/test1/': 'https://127.0.0.1:8000/test-pages/test1',
                '/test-pages/test2': 'https://127.0.0.1:8001/test-pages/test2',
                '/test-pages/test2/': 'https://127.0.0.1:8001/test-pages/test2',
                '/test-pages/test3': 'https://127.0.0.1:8002/test-pages/test3',
                '/test-pages/test3/': 'https://127.0.0.1:8002/test-pages/test3',
               }

    netAddresses = {'/': 'http://www.cnn.com:8000',
                    'www.cnn.com' : 'http://www.cnn.com:8000', 
                   #'http://www.cnn.com/': 'https://127.0.0.1:8001/test-pages/test2',
                   #'nothing.net': 'https:127.0.0.1:8002/test-pages/test3',
                  }

    page_get_fail = 'http://www.thisaddressdoesnotexist.com'

    def do_HEAD(self):
        host = self.headers.get('Host')
        self.send_response(301)
        print 'Current path in My request: ', self.path
        print 'Current Host in My request: ', host
        self.send_header('Location', self.netAddresses.get(host, self.page_get_fail))
        self.end_headers()

    def do_GET(self):
#        self.do_HEAD()           #used for forwarding to SSL Virtual servers
        self.response() 
    #host_head is used for http virtual hosting. If a blacklisted request is redirected to 127.0.0.1 then it is
    #resolved here and displayed while staying on port 80. Example cnn.com or foo.com
    def host_head(self):
        host = self.headers.get('Host')
        hostLinks = host.split('.')
        hostPath = hostLinks[0] + '/' + hostLinks[1] + '/' + hostLinks[2]
        f = None
        if os.path.isdir(hostPath):
            for index in 'index.html', 'index.htm':
                index = os.path.join(hostPath, index)
                if os.path.exists(index):
                    path = index
                    break
        try: #Use open with 
            basePath = path[:-10]
            index = path[24:]
            path  = basePath + './' + index
            print '2 Path: ', path
            f = open(path, 'rb')                            #F object needs to pass contents not, open file
        except IOError:
            self.send_error(404, 'File not found')
            return None
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        fs = os.fstat(f.fileno())
        self.send_header('Content-Length', str(fs.st_size))      #Used for TCP connections
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def response(self):
        f = self.host_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

def VirtualHandler(serverType=None, webURL=None):

    class VSHandler(BaseHTTPServer.BaseHTTPRequestHandler):

        server_version = serverType
        sys_version = ''

        def do_head(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def send_head(self):
            path = self.translate_path(self.path)
            f = None
            if os.path.isdir(path):
                if not self.path.endswith('/'):
                    self.send_response(301)
                    self.send_header('Location', self.path + '/')
                    self.end_headers()
                    return None
                for index in 'index.html', 'index.htm':
                    index = os.path.join(path, index)
                    if os.path.exists(index):
                        path = index
                        break
        #take the path of  the index found from the executed file and use it as the root directory
        #need to use relative paths for code portability
            try:                                                #Use open with 
                pathLinks = path.split('.')
                path = pathLinks[0]
                path = path[:-1] + self.path + '.' + pathLinks[1] + '.' + pathLinks[2]    
                f = open(path, 'rb')                            #F object needs to pass contents not, open file
            except IOError:
                self.send_error(404, 'File not found')
                return None
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            fs = os.fstat(f.fileno())
            self.send_header('Content-Length', str(fs.st_size))      #Used for TCP connections
            self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f

        def host_head(self):
            host = self.headers.get('Host')
            hostLinks = host.split('.')
            hostPath = hostLinks[0] + '/' + hostLinks[1] + '/' + hostLinks[2]
            f = None
            if os.path.isdir(hostPath):
                if not hostPath.endswith('/'):
                    self.send_response(301)
                    self.send_header('Location', hostPath + '/')
                    self.end_headers()
                    return None
                for index in 'index.html', 'index.htm':
                    index = os.path.join(hostPath, index)
                    if os.path.exists(index):
                        path = index
                        break
            try:                                                #Use open with 
                pathLinks = path.split('.')
                path = pathLinks[0]
                path = path[:-1] + hostPath + '.' + pathLinks[1] + '.' + pathLinks[2]    
                f = open(path, 'rb')                            #F object needs to pass contents not, open file
            except IOError:
                self.send_error(404, 'File not found')
                return None
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            fs = os.fstat(f.fileno())
            self.send_header('Content-Length', str(fs.st_size))      #Used for TCP connections
            self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f

        def translate_path(self, path):                         #Non-inherited objects should be private
            path = path.split('/',1)[0]
            path = path.split('#',1)[0]
            path = posixpath.normpath(urllib.unquote(path))
            words = path.split('/')
            words = filter(None,words)
            path = os.getcwd()
            for word in words:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word  in (os.curdir, os.pardir):
                    path = os.path.join(path, word)
            return path

        #consider moving to util.py
        def copyfile(self, source, outputfile):
            shutil.copyfileobj(source, outputfile)

        def response(self):
             f = self.send_head()
             if f:
                 self.copyfile(f, self.wfile)
                 f.close()

        def do_GET(self):
            print 'Current web URL: ', webURL
            host = self.headers.get('Host')
            if self.path == webURL:
                self.response()
            elif self.path == webURL + '/':
                self.response()
            else:
                self.send_error(404, 'File not found: %s'% self.path)

    return VSHandler


class RunTimeItems(object):
    def __init__(self, whiteList=None, blackList=None, saveOption=None):
        self.whitelist = whiteList
        self.blacklist = blackList
        self.save = saveOption

    def setLists(self):
        if self.save is None and (self.blacklist is not None or self.whitelist is not None):
             print 'Skipping list save for Wf and Bf'
             return
        else:
            temp = IOitems()
            items = temp.loadConfig()
            self.whitelist = items['Whitelist']
            self.blacklist = items['Blacklist']

class IOitems(object):
    def __init__(self, port=53, hport=None, hsport=None, saveOption=None, wFile=None, bFile=None):
        self.port = port
        self.http_port = hport
        self.https_port = hsport
        self.save = saveOption
        self.whitelist = wFile
        self.blacklist = bFile
    
    def setLists(self):
        if self.save == False and (self.http_port is not None or self.https_port is not None):
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
           #print 'Currentfile: ' + currentFile + '  Port: ' + str(DNSport) + '  Whitelist: '+ str(whiteFile) + '  Blacklist: ' + str(blackFile)
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
            self.save = save

    def set_wFile(self, inFile):
        if inFile is not None:
             self.whitefile = inFile

    def set_bFile(self, inFile):
        if inFile is not None:
             self.blackfile = inFile

    def startServers(self):
        #Port for either services will be set at launch on terminal or config file
        # run the DNS services
        myController = Controller.Controller(self)
        self.launchOptions()
        server = [SocketServer.ThreadingUDPServer(('', self.port), myController.UDPRequestHandler),]
        thread = threading.Thread(target=server[0].serve_forever)
        thread.daemon = True
        thread.start()
        print 'UDP server loop running on port ' + str(self.port) #in thread: %s % (thread.name)

        #Initialize and run HTTP services
        self.setLists()
        http_server = Http_start(self.http_port)
        http_server.daemon = True
        http_server.start()

        #initialize and run HTTPS services
        https_server = Https_start(self.https_port)
        https_server.daemon = True
        https_server.start()
        
        #Move these items to the config file
        certs = [#'server.key',
                 '/Users/ricardocarretero/dev/vm/ubuntu1404/certs/./test1cert.pem',
                 '/Users/ricardocarretero/dev/vm/ubuntu1404/certs/./test2cert.pem',
                 '/Users/ricardocarretero/dev/vm/ubuntu1404/certs/./test3cert.pem']

        keys = [# './server.crt',
                 '/Users/ricardocarretero/dev/vm/ubuntu1404/certs/./test1key.pem',
                 '/Users/ricardocarretero/dev/vm/ubuntu1404/certs/./test2key.pem',
                 '/Users/ricardocarretero/dev/vm/ubuntu1404/certs/./test3key.pem']
        ports = [#443, 
                 8000, 8001, 8002]
        VS_servers = []
        serverNames = ['nginx', 'IIS', 'Apache', 'gws', 'lighttpd']
        URLs = ['/test-pages/test1', '/test-pages/test2', '/test-pages/test3']
        for number in range(len(keys)):
            VS_servers.append('VS' + str(number))
            VS_servers[number] = VS_host(ports[number], certs[number], keys[number], VirtualHandler(serverNames[number], URLs[number]), name= VS_servers[number])
            VS_servers[number].daemon = True
            VS_servers[number].start()

        try:
            while 1:
                time.sleep(1)
                sys.stderr.flush()
                sys.stdout.flush()

        except KeyboardInterrupt:
            pass
        finally:
               server[0].shutdown()
               print 'Server terminated by SIGINT'

    def launchOptions(self):
         parser = argparse.ArgumentParser(description='This program forwards DNS requests not found in the whitelist or blacklist')
         parser.add_argument('-dp', '--dns_port', help='select the port the DNS server runs on. Default port 53', type=int)
         parser.add_argument('-wf', '--whiteFile', help='specify the file to be used as the whitelist', type=str)
         parser.add_argument('-bf', '--blackFile', help='specify the file to be used as the blacklist', type=str)
         parser.add_argument('-hp', '--http_port', help='select the port the HTTP server runs on. Default port 80 or 8080', type=int)
         parser.add_argument('-s', '--save_option', help='saves the launch options selected in the config file, select yes or no', default=False, action='store_true')
         parser.add_argument('-hsp', '--https_port', help='select the port the HTTPS server runs on. Default port 443', type=int)
         parser.add_argument('-cf', '--readfile', help='select the config file to load and save from', type=str)
         arg = parser.parse_args()
         self.set_DNSport(arg.dns_port)
         self.set_wFile(arg.whiteFile)
         self.set_bFile(arg.blackFile)
         self.set_HTTPport(arg.http_port) #needed if value is set but did not want to save
         self.set_HTTPSport(arg.https_port)
         self.set_save(arg.save_option)
         if arg.save_option == True: #this function prevents the program from saving garbage values if only -s is selected without params
             nullChoices = 0         #if it is run without paramaters to save, don't save
             argSize = len(vars(arg)) - 1 #There is a -1 because -s is a save flag
             for value in vars(arg):
                 if getattr(arg, value) == None:
                     nullChoices = nullChoices + 1
             if arg.readfile == True and nullChoices < argSize:
                 print 'Saving to new config file'
                 self.writeToConfig(arg.readfile, str(arg.dns_port), arg.whiteFile, arg.blackFile, str(arg.http_port), str(arg.https_port))
             elif arg.readfile == False and nullChoices < argSize:
                 print 'Saving settings'
                 self.writeToConfig('config.ini', str(arg.dns_port), arg.whiteFile, arg.blackFile, str(arg.http_port), str(arg.https_port))
