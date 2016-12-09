import webbrowser
import traceback
import os
import time
import datetime
from Model import *


class View(object):
    def __init__(self, currentFile='log.txt'):
        self.currentFile = currentFile

    def terminalOut(self, message):
        print message 

    def terminalLog(self, message):
        print message

#    def loadFile(self, currentFile):
#        try:
#            with open(currentFile) as domains:
#                domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
#            return domainList
#        except IOError:
#            print 'File not found, specify a valid file'
#            sys.exit(1)

    def add_log(self, message):
        try:
            if message is not None:
#                with open(self.currentFile, 'r+') as domains:
#                    domainList = [tuple(map(str.strip, line.split(','))) for line in domains]
#                    dictList = dict(domainList)
                with open(self.currentFile, 'a+') as fileData:
                    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                    fileData.write(str(message) + ' ' + '    Timestamp: ' + now + '\n\n')
#                    print DomainItem.name + ' with IP ' + DomainItem.IP + ' has been added to the database'
        except IOError:
            print 'File not found, specify a valid file'
            sys.exit(1)
