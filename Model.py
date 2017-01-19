import SocketServer
import socket
import threading
import Queue
import sys
import Controller
import View
import SimpleHTTPServer
import BaseHTTPServer
import urllib
import posixpath
import ssl
import StringIO
from dnslib import *
from multiprocessing.dummy import Pool as ThreadPool
from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, load_certificate
from OpenSSL.SSL import TLSv1_METHOD, Context, Connection

class Server(object):
 
    def factory(self, name, port=None):
        if name == 'HTTP': return HTTPServer(port)
        elif name == 'HTTPS': return HTTPSServer(port)
        elif name == 'DNS': return DNSServer(port)
#        elif type == 'VShost': return VS_host(port)
        else: 'No such type ' + name

class BaseServer(threading.Thread):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        raise NotImplementedError

class DNSServer(BaseServer):
    def run(self):
        try:
            print 'DNS UDP server running at %s port' % (self.port)
            DNS_server = SocketServer.ThreadingUDPServer(('', self.port), Controller.Controller.UDPRequestHandler)
            DNS_server.serve_forever()
        except KeyboardInterrupt:
            DNS_server.server_close()

class HTTPServer(BaseServer):
    def run(self):
        try:
            print 'Serving HTTP at port %s' % (self.port)
            http = SocketServer.TCPServer(('', int(self.port)), View.BaseHandler)
            http.serve_forever()
        except KeyboardInterrupt:
            http.server_close()

class HTTPSServer(BaseServer):
    def run(self):
        try:
            print 'Serving HTTPS at port %s' % (self.port)
            https = BaseHTTPServer.HTTPServer(('', int(self.port)), View.HTTPShandler)
            https.socket = ssl.wrap_socket(https.socket, certfile='./server.crt', server_side=True, keyfile='server.key')
            https.serve_forever()
        except KeyboardInterrupt:
            https.close()

class VS_host(BaseServer):
    def __init__(self, port=None, cert=None, key=None, handler= None, name= ''):
        super(VS_host, self).__init__(port)
        self.cert = cert
        self.key = key
        self.handler = handler
        self.name = name

    def run(self):
        try:   #re-evaluate
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
#        except keepRunning():
            VS.close() #possible bug if item is not created

      #This function determines when the request pool for a site has been exhausted
#     def keepRunning(self):
#         if len(queue) == 0:
#             return False
#         else:
#              return True


class HandlerFactory(object):
    
    def factory(self, name):
        if name == 'nginx': return View.NginxServerHandler
        elif name == 'Apache': return View.ApacheServerHandler
        elif name == 'gws': return View.GwsServerHandler
        elif name == 'IIS': return View.IISServerHandler
        else:
            print '%s type of handler not found.' % (name)
        
def setLists(self):
    items = self.loadConfig()
    if self.save is None and (self.blacklist is not None or self.whitelist is not None):
#         print 'Skipping list save for Wf and Bf'
        if self.whitelist is not None and self.blacklist is None:
            self.blacklist = items['Blacklist']
        if self.blacklist is not None and self.whitelist is None:
            self.whitelist = items['Whitelist']
    else:
#         print 'List save for Wf and Bf'
        self.whitelist = items['Whitelist']
        self.blacklist = items['Blacklist']
    lists = self.whitelist, self.blacklist
    return lists
