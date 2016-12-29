import traceback
import shutil
from Model import *

#View is now in charge of displaying the index file.
#It recieves the file object and then passes it onto
#the view then file is closed after it is copied.
class View(object):

    def terminalOut(self, message):
        print message 

    def terminalLog(self, message):
        print message
   
    def response(self, source, destination):
        shutil.copyfileobj(source, destination)
            
