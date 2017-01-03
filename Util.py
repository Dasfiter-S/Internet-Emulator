import socket

class Util(object):

    def valid_addr(self, address):
       try:
           socket.inet_aton(address)
       except socket.error:
           return False
       
       return True
