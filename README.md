#Internet Emulator Version 1.00
--------------------------------

This is the first release of the Internet Emulator. This program is designed to filter DNS requests if set as the primary DNS. You have the ability to filter the DNS queries from a blacklist that redirects all requests specified on the blacklist to the localhost(127.0.0.1). This program also contains an HTTP and HTTPS server with their respective self certified certificates.

The HTTP server is running on the standard http port 80. The HTTPS server is running on the standard HTTPS port 443. The HTTP server supports Virtual hosting by accessing several websites using a single HTTP server. The HTTPS server supports the HTTPS Virtual Hosting equivalent. It does this by checking the name of the host request and passing it to the server so it can load that certificate instead of the default certificate for the HTTPS server.

Usage:

    Known supported systems: Linux Ubuntu and OSX 
    Untested: Windows systems of any type
    
    Navigate your console to where this program was extracted. If you wish to run the program with the default parameters simply run:
    
    sudo python Main.py
    
    The program will load the following default values: Config.ini for the config files, blacklist.txt for the blacklist, dnsCashe.txt for the whitelist, port 53 for the DNS server, port 80 for HTTP, port 443 for HTTPS. You can directly edit the config file to change the load values. The program also supports command line options to specify the following:
    
    '-dp' or '--dns_port' 
    '-wf' or '--whiteFile'
    '-bf' or '--blackFile'
    '-hp' or '--http_port'
    '-s' or '--save_option'
    '-hsp' or '--https_port'
    '-cf' or '--readfile'

