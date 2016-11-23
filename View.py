import webbrowser
import traceback
import os
from Model import *


class View(object):
    def __init__(self, bID = '2'):
        self.browserID = bID

    def terminalOut(self, message):
        print message 

    def terminalLog(self, message):
        print
        #write to log file
