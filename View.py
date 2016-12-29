import traceback
import shutil
from Model import *


class View(object):
#    def__init__(self, currentFile='log.txt'):
#        self.currentFile = currentFile

    def terminalOut(self, message):
        print message 

    def terminalLog(self, message):
        print message
   
    def response(self, source, destination):
        shutil.copyfileobj(source, destination)
            
