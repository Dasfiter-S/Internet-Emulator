import socket
import threading
import Model
import sys
import time
class ServerBase(threading.Thread):
    def __init__(self, port=None):
        threading.Thread.__init__(self)
        self.port = port
    
    def run(self):
        raise NotImplemented

class TestServer(ServerBase): 

    def run(self):
        print 'HTTP socket server running on port %d' % (self.port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', self.port))
        self.parseIncomingConnections(server)

    def parseIncomingConnections(self, current_server):
        while True:
            try:
                current_server.listen(5)
                connection, address = current_server.accept()
                print 'Incoming connection \n Address: %s' % (str(address))
#                data = connection.recv(1024)
#                str_data = bytes.decode(data)
#                print('Body: %s') % (str_data)
#                self.handler(str_data, connection)
                
                handler = Model.HandlerFactory()
                gws_handler = handler.factory('gws')
                gws_handler(connection, address, current_server)
                
                
            except KeyboardInterrupt:
                current_server.close()
                current_server.server_shutdown()
                sys.exit(1)
    
    def __generateHeaders(self, code, server_type='Test Cat'):
        header = ''
        if code is 200:
            header = 'HTTP/1.1 %d OK\n' % (code)
        elif code is 404:
            header = 'HTTP/1.1 %d Not Found\n' % (code)

        current_date = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        header += 'Date: %s\n' % (current_date)
        header += 'Server: %s\n' % (server_type)
        header += 'Connection: close\n\n'

        return header

    def handler(self, str_raw_request, connection):
        request_method = str_raw_request.split(' ')[0]
        if (request_method is 'GET') or (request_method is 'HEAD'):
            fiel_requested = string.split(' ')
            file_requested = file_requested[1]
            if file_requested is '/':
                print 'Serving index'
                file_requested = './index.html'
#                file_requested = 
                try:
                    with open(file_requested, 'rb') as file_handler:
                        if (request_method is 'GET'):
                            response_content = file_handler.read()
                    response_headers = self.__generateHeaders(200)
                except Exception as e:
                    print 'File not found'
                    response_headers = self.__generateHeaders(404)

                server_response = response_headers.encode()
                if request_method is 'GET':
                    server_response += respones_content
                connection.send(server_response)
                connection.close()

    def serve_page(self):
        host
                        
if __name__ == '__main__':
    server = TestServer(80)
    server.daemon = True
    server.start()
    try:
        while True:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()
    except KeyboardInterrupt:
        sys.exit(1)


