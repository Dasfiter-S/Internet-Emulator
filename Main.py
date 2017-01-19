import argparse
from Controller import *
from Model import *


def launchOptions(mainObj):
    parser = argparse.ArgumentParser(description='This program forwards DNS requests not found in the whitelist or blacklist')
    parser.add_argument('-dp', '--dns_port', help='select the port the DNS server runs on. Default port 53', type=int)
    parser.add_argument('-wf', '--whiteFile', help='specify the file to be used as the whitelist', type=str)
    parser.add_argument('-bf', '--blackFile', help='specify the file to be used as the blacklist', type=str)
    parser.add_argument('-hp', '--http_port', help='select the port the HTTP server runs on. Default port 80 or 8080', type=int)
    parser.add_argument('-s', '--save_option', help='saves the launch options selected in the config file, select yes or no', default=False, action='store_true')
    parser.add_argument('-hsp', '--https_port', help='select the port the HTTPS server runs on. Default port 443', type=int)
    parser.add_argument('-cf', '--readfile', help='select the config file to load and save from', type=str)
    arg = parser.parse_args()
    mainObj.set_DNSport(arg.dns_port)
    mainObj.set_wFile(arg.whiteFile)
    mainObj.set_bFile(arg.blackFile)
    mainObj.set_HTTPport(arg.http_port) #needed if value is set but did not want to save
    mainObj.set_HTTPSport(arg.https_port)
    mainObj.set_save(arg.save_option)
#    Model.setLists(arg.whiteFile, arg.blackFile, arg.save_option)
    if arg.save_option == True: #this function prevents the program from saving garbage values if only -s is selected without params
        nullChoices = 0         #if it is run without paramaters to save, don't save
        argSize = len(vars(arg)) - 1 #There is a -1 because -s is a save flag
        for value in vars(arg):
            if getattr(arg, value) == None:
                nullChoices = nullChoices + 1
        if arg.readfile == True and nullChoices < argSize:
            print 'Saving to new config file'
            self.writeToConfig(arg.readfile, str(arg.dns_port), arg.whiteFile, arg.blackFile, str(arg.http_port), str(arg.https_port))
        elif arg.readfile == False and nullChoices < argSize:
            print 'Saving settings'
            self.writeToConfig('config.ini', str(arg.dns_port), arg.whiteFile, arg.blackFile, str(arg.http_port), str(arg.https_port))

def keepRunning():
    running = False
    try:
        running = True
    except KeyboardInterrupt:
        running = False
    return running

if __name__ == '__main__':
    print 'Starting DNS server! '
    mainItem = IOitems()
    launchOptions(mainItem)
    Model.setLists(mainItem)
    mainItem.startServers()
    while(keepRunning()):
        pass

        

#move config.ini to main
#ping the servers for time out and check if it exists if not continue
#server_is_up for pinging
#timeout for ping in config.ini
