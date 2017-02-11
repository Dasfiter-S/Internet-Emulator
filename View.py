import BaseHTTPServer
import SimpleHTTPServer
import traceback
import shutil
import logging
import Util
import re
import os
import time
import json
   
    #Pass View instance to other files, so they can share the same logger
    
    #Specify what part of the code generated the log

class BaseHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = ''
    sys_version = ''

    def do_GET(self):
        self.serve_page()
    
    #host_head is used for http virtual hosting. If a blacklisted request is redirected to 127.0.0.1 then it is
    #resolved here and displayed while staying on port 80. Example cnn.com or foo.com
    def serve_page(self):
        location = ''
        logging.debug('Serving GET request')
        host = self.headers.get('Host')
        logging.debug('Current host: %s' % (host))
        logging.debug('Headers: %s' % (self.headers))
        tool = Util.Util()
        #filter out IP address that cannot be parsed as localhost file paths
        if not tool.valid_addr(host): 
            if 'http://' in host:
                host = host.split('http://')[1]
            sub_string = re.search('\Awww', host)
            if sub_string is not None:
                if 'www'  not in sub_string.group(0):
                    host = 'www.%s' % (host)
            hostPath = re.sub('\.', '/', host)
            if os.path.isdir(hostPath):
                for index in 'index.html', 'index.htm':
                    index = os.path.join(hostPath, index)
                    if os.path.exists(index):
                        location = index
                        break
            try:
                location = re.sub('/index', '/./index', location)
                logging.debug('Index location: %s' % (location))
                with open(location, 'rb') as f:
                     self.send_response(200)
                     self.send_header('Content-type', 'text/html')
                     fs = os.fstat(f.fileno())
                     self.send_header('Content-Length', str(fs.st_size))      
                     self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
                     self.end_headers()
                     shutil.copyfileobj(f, self.wfile)

            except IOError:
                logging.error('404 File not found')
                self.send_error(404, 'File not found')
        else:
            logging.error('404 Address %s not found' % (host))
            self.send_error(404, 'The address %s was not found' % (host))


class NginxServerHandler(BaseHandler):
    server_version = 'nginx'

class ApacheServerHandler(BaseHandler):
    server_version = 'Apache'

class GwsServerHandler(BaseHandler):
    server_version = 'gws'

class IISServerHandler(BaseHandler):
    server_version = 'IIS'

class HTTPShandler(object):
    def __init__(self, str_request, client_connection, host_name, server_type='Test cat'):
        self.request = str_request
        self.connection = client_connection
        self.host = host_name
        self.server = server_type
#------------------------------------------------Move to JSON file
    def __generateHeaders(self, code):
        header = ''
        if code is 200:
            header = 'HTTP/1.1 %d OK\n' % (code)
        elif code is 404:
            header = 'HTTP/1.1 %d Not Found\n' % (code)
        current_date = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        header += 'Date: %s\n' % (current_date)
        header += 'Server: %s\n' % (self.server)
        header += 'Connection: close\n\n'
        return header
#-----------------------------------------------------------------
    def handler(self):
        response_content = ''
        request_method = self.request.split(' ')[0]
        if (request_method == 'GET') or (request_method == 'HEAD'):
            file_requested = self.request.split(' ')
            file_requested = file_requested[1]
            print 'Request type: %s' % (request_method)
            if file_requested == '/':
                subString = re.search('\Awww', self.host)
                if subString is not None:
                    if 'www' not in subString.group(0):
                        self.host = 'www.%s' % (self.host)
                hostPath = re.sub('\.', '/', self.host)
                if os.path.isdir(hostPath):
                    for index in 'index.html', 'index.htm':
                        index = os.path.join(hostPath, index)
                        if os.path.exists(index):
                            location = index
                            break
                try:
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
                    server_response += response_content
                self.connection.sendall(server_response)

