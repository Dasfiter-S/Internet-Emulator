import SocketServer
import socket
import threading
import Queue
import sys
import Controller
import View
import os
import SimpleHTTPServer
import BaseHTTPServer
import urllib
import posixpath
import shutil
import ssl
import StringIO
import Util
from dnslib import *
from multiprocessing.dummy import Pool as ThreadPool
from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, load_certificate
from OpenSSL.SSL import TLSv1_METHOD, Context, Connection

class Server(threading.Thread):
 
    def factory(self, type, port=None):
        if type == 'HTTP': return Http_start(port)
        elif type == 'HTTPS': return Https_start(port)
#        elif type == 'VShost': return VS_host(port)
        else: 'No such type ' + type


class Http_start(Server):
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

class Https_start(Server):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        try:
            print 'Serving HTTPS at port', self.port
            https = BaseHTTPServer.HTTPServer(('', int(self.port)), RedirectHandler)
            https.socket = ssl.wrap_socket(https.socket, certfile='./server.crt', server_side=True, keyfile='server.key')
            https.serve_forever()
        except KeyboardInterrupt:
            https.close()

class VS_host(Server):
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

#This handler is not using the factory pattern since it is the initial gate
#for redirection if needed.
class RedirectHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    server_version = 'gws'
    sys_version = ''

    #THese lists will be moved to a file
    pathways = {'/test-pages': 'https://127.0.0.1/test-pages', 
                '/test-pages/': 'https://127.0.0.1/test-pages/',
                '/test-pages/test1': 'https://127.0.0.1:8000/test-pages/test1',
                '/test-pages/test1/': 'https://127.0.0.1:8000/test-pages/test1',
                '/test-pages/test2': 'https://127.0.0.1:8001/test-pages/test2',
                '/test-pages/test2/': 'https://127.0.0.1:8001/test-pages/test2',
                '/test-pages/test3': 'https://127.0.0.1:8002/test-pages/test3',
                '/test-pages/test3/': 'https://127.0.0.1:8002/test-pages/test3',
               }

    netAddresses = {'cnn.com': 'https://www.cnn.com:8000',
                    'www.cnn.com' : 'https://www.cnn.com:8000',
                    'foo.com' : 'https://www.foo.com:8001',
                    'www.foo.com' : 'https://www.foo.com:8001',
                  }

    page_get_fail = 'http://www.thisaddressdoesnotexist.com'
    
    #Used only for redirects, otherwise not called
    def _do_HEAD(self):
        host = self.headers.get('Host')
        self.send_response(301)
        self.send_header('Location', self.netAddresses.get(host, self.page_get_fail))
        self.end_headers()

    def do_GET(self):
        self._do_HEAD()           #used for forwarding to SSL Virtual servers, next step is to get HTTPS working

class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    server_version = 'nginx'
    sys_version = ''


    def do_GET(self):
        self.__host_head() 

    #host_head is used for http virtual hosting. If a blacklisted request is redirected to 127.0.0.1 then it is
    #resolved here and displayed while staying on port 80. Example cnn.com or foo.com
    def __host_head(self):
        host = self.headers.get('Host')
        tool = Util.Util()
        if not tool.valid_addr(host): #filter out IP address that cannot be parsed as localhost file paths
            if 'www' in host:
                hostLinks = host.split('.')
                hostPath = hostLinks[0] + '/' + hostLinks[1] + '/' + hostLinks[2]
            else:
                host = 'www.' + host
                hostLinks = host.split('.')
                hostPath = hostLinks[0] + '/' + hostLinks[1] + '/' + hostLinks[2]
            if os.path.isdir(hostPath):
                for index in 'index.html', 'index.htm':
                    index = os.path.join(hostPath, index)
                    if os.path.exists(index):
                        path = index
                        break
            try: 
                pathParts = path.split('index')
                basePath = pathParts[0]
                index = pathParts[1] 
                path  = basePath + './index' + index
                with open(path, 'rb') as f:
                     self.send_response(200)
                     self.send_header('Content-type', 'text/html')
                     fs = os.fstat(f.fileno())
                     self.send_header('Content-Length', str(fs.st_size))      #Used for TCP connections
                     self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
                     self.end_headers()
                     show = View.View()
                     show.response(f, self.wfile)

            except IOError:                                     
                self.send_error(404, 'File not found')
        else:
            self.send_error(404, 'The address ' + str(host) + ' was not found')


def VirtualHandler(serverType=None, webURL=None):

    class VSHandler(BaseHTTPServer.BaseHTTPRequestHandler):

        server_version = serverType
        sys_version = ''

        def __send_head(self):
            path = self.__translate_path(self.path)
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
        #take the path of the index found from the executed file and use it as the root directory
        #need to use relative paths for code portability
            try:  
                if not socket.inet_aton(self.path):
                    pathLinks = path.split('.')
                    path = pathLinks[0]
                    path = path[:-1] + self.path + '.' + pathLinks[1] + '.' + pathLinks[2]
                else:
                    self.send_error(404, 'File not found', )
                with open(path, 'rb') as f:
                     self.send_response(200)
                     self.send_header('Content-type', 'text/html')
                     fs = os.fstat(f.fileno())
                     self.send_header('Content-Length', str(fs.st_size))      #Used for TCP connections
                     self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
                     self.end_headers()
                     show = View.View()
                     show.response(f, self.wfile)

            except IOError:
                self.send_error(404, 'File not found')
                return None

        def __host_head(self):
            host = self.headers.get('Host')
            tool = Util.Util()
            if not tool.valid_addr(host): #filter out IP address that cannot be parsed as localhost file paths
                if ':' in host:
                    host_split = host.split(':')
                    host = host_split[0]
                if 'www' in host:
                    hostLinks = host.split('.')
                    hostPath = hostLinks[0] + '/' + hostLinks[1] + '/' + hostLinks[2]
                else:
                    host = 'www.' + host
                    hostLinks = host.split('.')
                    hostPath = hostLinks[0] + '/' + hostLinks[1] + '/' + hostLinks[2]
                if os.path.isdir(hostPath):
                    for index in 'index.html', 'index.htm':
                        index = os.path.join(hostPath, index)
                        if os.path.exists(index):
                            self.path = index
                            break
                try: 
                    pathParts = self.path.split('index') #replace index
                    basePath = pathParts[0]
                    index = pathParts[1] 
                    path  = basePath + './index' + index
                    with open(self.path, 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        fs = os.fstat(f.fileno())
                        self.send_header('Content-Length', str(fs.st_size))      #Used for TCP connections
                        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
                        self.end_headers()
                        show = View.View() #single
                        show.response(f, self.wfile)
                except IOError:                                     
                    self.send_error(404, 'File not found')
            else:
                self.send_error(404, 'The address ' + str(host) + ' was not found')


        def __translate_path(self, path):                         #Non-inherited objects should be private
            path = path.split('/',1)[0]
            path = path.split('#',1)[0]
            path = posixpath.normpath(urllib.unquote(path))
            words = path.split('/')
            words = filter(None, words)
            path = os.getcwd()
            for word in words:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word  in (os.curdir, os.pardir):
                    path = os.path.join(path, word)
            return path


        def do_GET(self):
            print 'Current web URL: ', webURL
            self.__host_head()

    return VSHandler


class RunTimeItems(object):
    def __init__(self, whiteList=None, blackList=None, saveOption=None):
        self.whitelist = whiteList
        self.blacklist = blackList
        self.save = saveOption

    def setLists(self):
        self.whitelist = IOitems.whitelist
        self.blacklist = IOitems.blacklist
        self.save = IOitems.saveOp
        print 'set Save: ', self.save
        print 'set Blacklist: ', self.blacklist
        print 'set Whitelist: ', self.whitelist
        temp = IOitems()
        items = temp.loadConfig()
        if self.save is None and (self.blacklist is not None or self.whitelist is not None):
             print 'Skipping list save for Wf and Bf'
             if self.whitelist is not None and self.blacklist is None:
                 self.blacklist = items['Blacklist']
             if self.blacklist is not None and self.whitelist is None:
                 self.whitelist = items['Whitelist']
             return
        else:
             print 'List save for Wf and Bf'
             self.whitelist = items['Whitelist']
             self.blacklist = items['Blacklist']

