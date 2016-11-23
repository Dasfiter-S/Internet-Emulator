import Queue
from Controller import *
from Model import *

if __name__ == '__main__':
    print 'Starting DNS server! '
    queue = Queue.Queue()
    myController = Controller()
    myController.launchOptions()
    mainItem = IOitems()
    mainItem.startServer(myController)
