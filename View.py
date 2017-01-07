import traceback
import shutil
import logging

#View is now in charge of displaying the index file.
#It recieves the file object and then passes it onto
#the view then file is closed after it is copied.
class View(object):

    def response(self, source, destination):
        shutil.copyfileobj(source, destination)
    
    #create a log that is shared between all files 
    def startLog(filename='Inet_emulator.log', level=logging.DEBUG):
        logging.basicConfig(filename, level)

    
    #Pass View instance to other files, so they can share the same logger
    
    #Specify what part of the code generated the log

    #
