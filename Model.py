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
import logging
import Util

import re
import OpenSSL

from dnslib import *
from multiprocessing.dummy import Pool as ThreadPool
from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, load_certificate
from OpenSSL.SSL import TLSv1_METHOD, Context, Connection


class Server(object):
 
    def factory(self, name, port=None):
        if name == 'HTTP': return HTTPServer(port)
        elif name == 'HTTPS': return HTTPSServer(port)
        elif name == 'DNS': return DNSServer(port)
        elif name == 'Easy': return EasyHTTPSServer(port)
        else:
            logging.debug('No such type %s' % (name))
            print 'No such type %s' % (name)

class BaseServer(threading.Thread):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        raise NotImplementedError

class DNSServer(BaseServer):
    def run(self):
        try:
            print 'DNS UDP server running on %s port' % (self.port)
            logging.debug('DNS server running on %s port' % (self.port))
            DNS = SocketServer.ThreadingUDPServer(('', self.port), Controller.Controller.UDPRequestHandler)
            DNS.serve_forever()
        except KeyboardInterrupt:
            raise KeyboardInterrupt
            DNS.shutdown()
            DNS.server_close()

class HTTPServer(BaseServer):
    def run(self):
        try:
            print 'Serving HTTP at port %s' % (self.port)
            logging.debug('Serving HTTP at port %s' % (self.port))
            http = SocketServer.TCPServer(('', int(self.port)), View.BaseHandler)
            http.serve_forever()
        except KeyboardInterrupt:
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
                server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                server_context.load_cert_chain(certfile=tool.get_path('/certs/test1cert.pem'),
                                               keyfile=tool.get_path('/certs/test1key.pem'))
                connstream = server_context.wrap_socket(connection, server_side=True)
                data = connstream.read()
                host = self.processHost(data)
                self.__do_SNI(address, host, connstream, current_server, data, connection)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
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
            server_ssl.set_context(new_context)
            print server_ssl.get_state_string()
            print 'Processing data after accept'
            self.handler(data_in, connstream, host)
            connstream.shutdown(socket.SHUT_RDWR)
            connstream.close()

    def processHost(self, data_in):
        host = re.search('(?<=Host: ).*', data_in)
        if host is not None:
           host = host.group()
           host = host.rstrip()
           if 'www' not in host:
               host = 'www.%s' % (host)
           return host

#--------------Move to model
    def __loadKey(self, path, tool):
        with open(tool.get_path(path), 'rb') as key:
            return OpenSSL.crypto.load_privatekey(OpenSSL.SSL.FILETYPE_PEM, key.read())

    def __loadCert(self, path, tool):
        with open(tool.get_path(path), 'rb') as cert:
            return OpenSSL.crypto.load_certificate(OpenSSL.SSL.FILETYPE_PEM, cert.read())
#---------------------------------

    #Fully custom non-inherited handler for webpages    
    def __generateHeaders(self, code, server_type='Test Cat'):
        header = ''
        if code is 200:
            header = 'HTTP/1.1 %d OK\n' % (code)
        elif code is 404:
            header = 'HTTP/1.1 %d Not Found\n' % (code)
        current_date = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        header += 'Date: %s\n' % (current_date)
        header += 'Server: %s\n' % (server_type)
        header += 'Connection: closed\n\n'
        return header

    def handler(self, str_raw_request, connection, host):
        response_content = ''
        request_method = str_raw_request.split(' ')[0]
        if (request_method == 'GET') or (request_method == 'HEAD'):
            file_requested = str_raw_request.split(' ')
            file_requested = file_requested[1]
            print 'Request type: %s' % (request_method)
            if file_requested == '/':
                print 'Current host', host
                subString = re.search('\Awww', host)
                print 'Current substring', subString
                if subString is not None:
                    if 'www' not in subString.group(0):
                        host = 'www.%s' % (host)
                hostPath = re.sub('\.', '/', host)
                if os.path.isdir(hostPath):
                    print 'Finding index'
                    for index in 'index.html', 'index.htm':
                        index = os.path.join(hostPath, index)
                        if os.path.exists(index):
                            location = index
                            break
                try:
                    print 'Loading index'
                    print location
                    location = re.sub('/index', '/./index', location)
                    with open(location, 'rb') as file_handler:
                        if (request_method == 'GET'):
                            print 'Fetching index to serve'
                            response_content = file_handler.read()
                    print 'Sending response 200'
                    response_headers = self.__generateHeaders(200)
                except Exception as e:
                    print 'File not found'
                    response_headers = self.__generateHeaders(404)

                server_response = response_headers.encode()
                if request_method == 'GET':
                    print 'Serving html response with content'
                    server_response += response_content
                connection.sendall(server_response)

class EasyHTTPSServer(BaseServer):
    def run(self):
        try:
            print 'Serving HTTPS at port %s' % (self.port)
            logging.debug('Serving HTTPS at port %s' % (self.port))
            https = BaseHTTPServer.HTTPServer(('', int(self.port)), View.HTTPShandler)
            https.socket = ssl.wrap_socket(https.socket, certfile='./server.crt', server_side=True, keyfile='server.key')
            https.serve_forever()
        except KeyboardInterrupt:
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
        if name == 'HTTPS': return View.HTTPSHandler
        else:
            logging.debug('%s type of handler not found.' % (name))
            print '%s type of handler not found.' % (name)

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
