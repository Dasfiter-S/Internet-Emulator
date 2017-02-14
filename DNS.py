import Model
import Controller
import time
import sys

#This the standalone for the DNS server
 
def keepRunning():
    running = True
    try:
        running = True 
    except (KeyboardInterrupt, SystemExit):
        running = False
        raise
    return running

if __name__ == '__main__':
    tmp = Controller.IOitems()
    items = tmp.loadConfig()
    server = Model.Server()
    dns_server = server.factory('DNS', int(items['DNSport'])) 
    dns_server.daemon = True
    dns_server.start()
    try:
        while(keepRunning()):
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()
    except (KeyboardInterrupt, SystemExit):
        print 'Terminated via SIGNINT'
        sys.exit(1)

