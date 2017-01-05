import socket
import os

class Util(object):
    
    def get_path(self, relative_path):
        full_path = os.path.dirname(os.path.abspath(__file__))
        return(full_path + relative_path)

    def valid_addr(self, address):
       try:
           socket.inet_aton(address)
       except socket.error:
           return False
       
       return True
