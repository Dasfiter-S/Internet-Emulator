import SocketServer
import socket
import threading
import sys
import Controller
import View
import BaseHTTPServer
import ssl
import logging
import Util
import re
import OpenSSL
from dnslib import *


class Server(object):
 
    def factory(self, name, port=None):
        if name == 'HTTP': return HTTPServer(port)
        elif name == 'HTTPS': return HTTPSServer(port)
        elif name == 'DNS': return DNSServer(port)
        elif name == 'Easy': return EasyHTTPSServer(port)
        else:
            logging.debug('No such type %s' % (name))
            print 'No such type %s' % (name)
#Virtual Class, only inherit from this class
class BaseServer(threading.Thread):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        raise NotImplementedError
#DNS only, server type
class DNSServer(BaseServer):
    def run(self):
        try:
            print 'DNS UDP server running on %s port' % (self.port)
            logging.debug('DNS server running on %s port' % (self.port))
            DNS = SocketServer.ThreadingUDPServer(('', self.port), Controller.Controller.UDPRequestHandler)
            DNS.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            DNS.shutdown()
            DNS.server_close()
            sys.exit(1)
 
class HTTPServer(BaseServer):
    def run(self):
        try:
            print 'Serving HTTP at port %s' % (self.port)
            logging.debug('Serving HTTP at port %s' % (self.port))
            http = SocketServer.TCPServer(('', int(self.port)), View.BaseHandler)
            http.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            http.shutdown()
            http.server_close()

class HTTPSServer(BaseServer):
    def run(self):
        print 'HTTP socket server running on port %s' % (self.port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', int(self.port)))
        server.listen(5)
        self.__parseIncomingConnections(server)

    def __parseIncomingConnections(self, current_server):
        while True:
            try:
                connection, address = current_server.accept()
                print 'Incoming connection \n Address: %s' % (str(address))
                tool = Util.Util()
                server_context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)
                server_context.set
                server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                server_context.load_cert_chain(certfile=tool.get_path('/certs/test1cert.pem'),
                                               keyfile=tool.get_path('/certs/test1key.pem'))
                connstream = server_context.wrap_socket(connection, server_side=True)
                data = connstream.read()
                host = self.processHost(data)
                self.__do_SNI(address, host, connstream, current_server, data, connection)
            except (KeyboardInterrupt, SystemExit):
                connstream.shutdown(socket.SHUT_RDWR)
                connstream.close()
                sys.exit(1)

    def __do_SNI(self, addr, host, connstream, server, data_in, conn):
        tool = Util.Util()
        new_context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)
        if host is not None:
            new_context.use_certificate(self.__loadCert('/certs/%s.cert' % (host), tool))
            new_context.use_privatekey(self.__loadKey('/certs/%s.key' % (host), tool))
            server_ssl = OpenSSL.SSL.Connection(new_context, server)
#            server_ssl.connect(('', int(self.port)))
            new_stream = server_ssl.wrap_socket(conn, server_side=True)
            print server_ssl.get_state_string()
            print 'Processing data after accept'
            #passing data to the handler
            virtual_handler = HandlerFactory()
            handler = virtual_handler.https_factory()
            https_handler = handler(data_in, new_stream, host)
            https_handler.handler()

            #connstream.shutdown(socket.SHUT_RDWR)
            #connstream.close()

    def __do_SNI2(self, addr, host, connstream, server, data_in, conn):
        tool = Util.Util()
        if host is not None:
                new_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                new_context.load_cert_chain(certfile=tool.get_path('/certs/%s.cert' % (host)),
                                               keyfile=tool.get_path('/certs/%s.key' % (host)))
                new_stream = new_context.wrap_socket(conn, server_side=True)
                print new_context.get_state_string()
                virtual_handler = HandlerFactory()
                handler = virtual_handler.https_factory()
                https_handler = handler(data_in, connstream, host)
                https_handler.handler()

    def processHost(self, data_in):
        host = re.search('(?<=Host: ).*', data_in)
        if host is not None:
            host = host.group()
            host = host.rstrip()
            #This part can be removed if the pre-append of www is not needed keep in
            #mind that the file path to load the index file is determined by the link.
            sub_string = re.search('\Awww', host)
            if sub_string is None:
                host = 'www.%s' % (host)
            return host

    def __loadKey(self, path, tool):
        with open(tool.get_path(path), 'rb') as key:
            return OpenSSL.crypto.load_privatekey(OpenSSL.SSL.FILETYPE_PEM, key.read())

    def __loadCert(self, path, tool):
        with open(tool.get_path(path), 'rb') as cert:
            return OpenSSL.crypto.load_certificate(OpenSSL.SSL.FILETYPE_PEM, cert.read())

class EasyHTTPSServer(BaseServer):
    def run(self):
        try:
            print 'Serving HTTPS at port %s' % (self.port)
            logging.debug('Serving HTTPS at port %s' % (self.port))
            https = BaseHTTPServer.HTTPServer(('', int(self.port)), View.HTTPShandler)
            https.socket = ssl.wrap_socket(https.socket, certfile='./server.crt', server_side=True, keyfile='server.key')
            https.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            https.shutdown()
            https.server_close()

class HandlerFactory(object):
    
    def http_factory(self, name):
        if name == 'nginx': return View.NginxServerHandler
        elif name == 'Apache': return View.ApacheServerHandler
        elif name == 'gws': return View.GwsServerHandler
        elif name == 'IIS': return View.IISServerHandler
        else:
            logging.debug('%s type of handler not found.' % (name))
            print '%s type of handler not found.' % (name)

    def https_factory(self):
        return View.HTTPShandler

def setLists(self):
    items = self.loadConfig()
    if self.save is None and (self.blacklist is not None or self.whitelist is not None):
#        print 'Skipping list save for Wf and Bf'
        logging.debug('Skipping list save for Whitefile and Blackfile')
        if self.whitelist is not None and self.blacklist is None:
            self.blacklist = items['Blacklist']
        if self.blacklist is not None and self.whitelist is None:
            self.whitelist = items['Whitelist']
    else:
#         print 'List save for Wf and Bf'
        logging.debug('Saving list for Whitefile and Blackfile')
        self.whitelist = items['Whitelist']
        self.blacklist = items['Blacklist']
    lists = self.whitelist, self.blacklist
    return lists
#---------------------------------------------Move to separate file to generate JSON header files
class GenerateHeaders(object):
    def __init__(self, code, server_type, fsize):
        self.http_code = code
        self.server = server_type
        self.file_length = fsize
        
    def makeHeaders(self):
        header = ''
        if self.http_code is 200:
            header = 'HTTP/1.1 %d OK\r\n' % (self.http_code)
        elif self.http_code is 404:
            header = ' HTTP/1.1 %d Not found\r\n' % (self.http_code)
        current_date = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        header += 'Date: %s\r\n' % (current_date)
        header += 'Server: %s\r\n' % (self.server)
        header += 'Content-Type: html\r\n'
        header += 'Content-Length: %s\r\n' % (self.file_length)
        header += 'Connection: close \r\n\n'
        data_string = json.dumps(header) 
        return data_string
#-----------------------------------------------
