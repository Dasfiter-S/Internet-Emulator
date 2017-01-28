import BaseHTTPServer
import SimpleHTTPServer
import traceback
import shutil
import logging
import Util
import re
import os

   
    #Pass View instance to other files, so they can share the same logger
    
    #Specify what part of the code generated the log

class BaseHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = ''
    sys_version = ''

    def do_GET(self):
        self.serve_page()
    
    def __SSL(self):
        test
        
    def __pick_certificate(self, host):
        host

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
            subString = re.search('\Awww', host)
            if subString is not None:
                if 'www'  not in subString.group(0):
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


class HTTPShandler(BaseHandler):

    #These lists will be moved to a file

    pathways = {'cnn.com': 'https://www.cnn.com:8000',
                    'www.cnn.com' : 'https://www.cnn.com:8000',
                    'foo.com' : 'https://www.foo.com:8001',
                    'www.foo.com' : 'https://www.foo.com:8001',
                  }
    port = []
    page_get_fail = 'http://www.google.com'
    
    #Overrides the base handler serve_page()
    def serve_page(self): 
        host = self.headers.get('Host')
#        print 'Headers: %s' % (self.headers)
        self.send_response(301)
        self.send_header('Location', 'https://%s:%s' % (host, '8000'))#self.port[0]))
        self.end_headers()

class NginxServerHandler(BaseHandler):
    server_version = 'nginx'

class ApacheServerHandler(BaseHandler):
    server_version = 'Apache'

class GwsServerHandler(BaseHandler):
    server_version = 'gws'

class IISServerHandler(BaseHandler):
    server_version = 'IIS'
