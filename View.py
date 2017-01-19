import BaseHTTPServer
import SimpleHTTPServer
import traceback
import shutil
import logging
import Util
import re
import os

class View(object):

    #create a log that is shared between all files 
    def startLog(filename='Inet_emulator.log', level=logging.DEBUG):
        logging.basicConfig(filename, level)

    
    #Pass View instance to other files, so they can share the same logger
    
    #Specify what part of the code generated the log

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
            subString = re.search('\Awww', host)
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
#                print 'Index: ', location
                location = re.sub('/index', '/./index', location)
                with open(location, 'rb') as f:
                     self.send_response(200)
                     self.send_header('Content-type', 'text/html')
                     fs = os.fstat(f.fileno())
                     self.send_header('Content-Length', str(fs.st_size))      #Used for TCP connections
                     self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
                     self.end_headers()
                     shutil.copyfileobj(f, self.wfile)

            except IOError:
                self.send_error(404, 'File not found')
        else:
            self.send_error(404, 'The address %s was not found' % (host))

class HTTPShandler(BaseHandler):

    #These lists will be moved to a file

    pathways = {'cnn.com': 'https://www.cnn.com:8000',
                    'www.cnn.com' : 'https://www.cnn.com:8000',
                    'foo.com' : 'https://www.foo.com:8001',
                    'www.foo.com' : 'https://www.foo.com:8001',
                  }

    page_get_fail = 'http://www.google.com'

    def serve_head(self):
        host = self.headers.get('Host')
        self.send_response(301)
#        self.__serverType(self.headers)
        #pass free port from where?
#        testPath = {host: 'https://%s:%s' % (host, free_port)}
        self.send_header('Location', self.pathways.get(host, self.page_get_fail))
        self.end_headers()

    def __serverType(self, in_header):
        handlerType = in_header.get('Server')
        #Pass handler to IOitems.startServers


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

