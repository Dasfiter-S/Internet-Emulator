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

class Server(object):
 
    def factory(self, name, port=None):
        if name == 'HTTP': return HTTPServer(port)
        elif name == 'HTTPS': return HTTPSServer(port)
#        elif type == 'VShost': return VS_host(port)
        else: 'No such type ' + name

class BaseServer(threading.Thread):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        raise NotImplementedError

class HTTPServer(BaseServer):
    def run(self):
        try:
            print 'Serving HTTP at port', self.port
            http = SocketServer.TCPServer(('', int(self.port)), BaseHandler)
            http.serve_forever()
        except KeyboardInterrupt:
            http.server_close()

class HTTPSServer(BaseServer):
    def run(self):
        try:
            print 'Seving HTTPS at port', self.port
            https = BaseHTTPServer.HTTPServer(('', int(self.port)), HTTPShandler)
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
                print 'HTTPS %s on port: %d ' % (self.name, self.port)
                VS = BaseHTTPServer.HTTPServer(('', int(self.port)), self.handler)
                VS.socket = ssl.wrap_socket(VS.socket, certfile= self.cert, server_side=True, keyfile= self.key)
                VS.serve_forever()
            else:
                print 'HTTP %s on port: %d ' % (self.name, self.port)
                VS = BaseHTTPServer.HTTPServer(('', int(self.port)), MyRequestHandler)
                VS.serve_forever()
        except KeyboardInterrupt:
            VS.close()

class BaseHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = ''
    sys_version = ''
    
    def do_GET(self):
        self.serve_head() 

    #host_head is used for http virtual hosting. If a blacklisted request is redirected to 127.0.0.1 then it is
    #resolved here and displayed while staying on port 80. Example cnn.com or foo.com
    def serve_head(self):
        host = self.headers.get('Host')
        tool = Util.Util()
        if not tool.valid_addr(host): #filter out IP address that cannot be parsed as localhost file paths
            if ':' in host:
                host = host.split(':')[0]
            if 'www' in host:
                hostLinks = host.split('.')
            else:
                host = 'www.%s' % (host)
                hostLinks = host.split('.')
            hostPath = '%s/%s/%s' % (hostLinks[0], hostLinks[1], hostLinks[2])
            if os.path.isdir(hostPath):
                for index in 'index.html', 'index.htm':
                    index = os.path.join(hostPath, index)
                    if os.path.exists(index):
                        location = index
                        break
            try: 
                print 'Index: ', location
                pathParts = location.split('index')
                basePath = pathParts[0]
                index = pathParts[1] 
                location  = '%s./index%s' % (basePath, index)
                with open(location, 'rb') as f:
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
            self.send_error(404, 'The address %s was not found' % (host))


class HTTPShandler(BaseHandler):
        
    #THese lists will be moved to a file

    pathways = {'cnn.com': 'https://www.cnn.com:8000',
                    'www.cnn.com' : 'https://www.cnn.com:8000',
                    'foo.com' : 'https://www.foo.com:8001',
                    'www.foo.com' : 'https://www.foo.com:8001',
                  }

    page_get_fail = 'http://www.thisaddressdoesnotexist.com'
    
    #Used only for redirects, otherwise not called
    def serve_head(self):
        host = self.headers.get('Host')
        self.send_response(301)
        self.send_header('Location', self.pathways.get(host, self.page_get_fail))
        self.end_headers()


class NginxServerHandler(BaseHandler):
    server_version = 'nginx'

class ApacheServerHandler(BaseHandler):
    server_version = 'Apache'

class GwsServerHandler(BaseHandler):
    server_version = 'gws'

class IISServerHandler(BaseHandler):
    server_version = 'IIS'

class HandlerFactory(object):
    
    def factory(self, name):
        if name == 'nginx': return NginxServerHandler
        elif name == 'Apache': return ApacheServerHandler
        elif name == 'gws': return GwsServerHandler
        elif name == 'IIS': return IISServerHandler
        else:
            print '%s type of handler not found.' % (name)
        
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


def setLists(self):
    if self is None:
        self = Controller.IOitems()
        items = self.loadConfig()
    else:
        print 'set Save: %s' % (self.save)
        print 'set Blacklist: %s' % (self.blacklist)
        print 'set Whitelist: %s' % (self.whitelist)
        items = self.loadConfig()
        if self.save is None and (self.blacklist is not None or self.whitelist is not None):
            print 'Skipping list save for Wf and Bf'
            if self.whitelist is not None and self.blacklist is None:
                self.blacklist = items['Blacklist']
            if self.blacklist is not None and self.whitelist is None:
                self.whitelist = items['Whitelist']
        else:
            print 'List save for Wf and Bf'
            self.whitelist = items['Whitelist']
            self.blacklist = items['Blacklist']
    lists = self.whitelist, self.blacklist
    return lists
