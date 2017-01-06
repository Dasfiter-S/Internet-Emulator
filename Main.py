import Queue
from Controller import *
from Model import *



if __name__ == '__main__':
    print 'Starting DNS server! '
    mainItem = IOitems()
    mainItem.launchOptions()
    mainItem.startServers()

