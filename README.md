#Internet Emulator Version 1.00
--------------------------------

This is the first release of the Internet Emulator. This program is designed to filter DNS requests if set as the primary DNS. You have the ability to filter the DNS queries from a blacklist that redirects all requests specified on the blacklist to the localhost(127.0.0.1). This program also contains an HTTP and HTTPS server with their respective self certified certificates.

The HTTP server is running on the standard http port 80. The HTTPS server is running on the standard HTTPS port 443. The HTTP server supports Virtual hosting by accessing several websites using a single HTTP server. The HTTPS server supports the HTTPS Virtual Hosting equivalent. It does this by checking the name of the host request and passing it to the server so it can load that certificate instead of the default certificate for the HTTPS server.

Usage:

    Known supported systems: Linux Ubuntu and OSX 
    Untested: Windows systems of any type
    
    Navigate your console to where this program was extracted. If you wish to run the program with the default parameters simply run:
    
    sudo python Main.py
    
    The program will load the following default values: Config.ini for the config files, blacklist.txt for the blacklist, dnsCache.txt for the whitelist, port 53 for the DNS server, port 80 for HTTP, port 443 for HTTPS. You can directly edit the config file to change the load values. The program also supports command line options to specify the following:
    
    sudo python Main.py [option]
    
    [options]:
    '-dp' or '--dns_port' select the dns port, defaults to 53
    '-wf' or '--whiteFile' specify the whitefile, defaults to dnsCache.txt
    '-bf' or '--blackFile' name the blackfile to use, defaults to blacklist.txt 
    '-hp' or '--http_port' select the port to run the http server on, defaults to 80
    '-s' or '--save_option' save options or run without saving options(strongly recommended to use save). Defaults to false
    '-hsp' or '--https_port' select the port to run the https server on, defaults to port 443
    '-cf' or '--readfile' choose the config file to use for loading, defaults to config.ini if file is not specified
    
    Example usage:
    
    sudo python Main.py -s -dp 8000 -hp 8001 -hsp 8002
                  set save, dns port 8000, http port, 8001, https port 8002
                  
    sudo python Main.py 
                  set no save, load all defaults from Config.ini
                  
    sudo python Main.py -s
                  set save, gets ignored since no values were chosen
                  
    sudo python Main.py -wf test.txt -bf test2.txt
                  set no save, whitelist to text.txt, set blackfile to test2.txt. This has some unexpected behavior as in the names of the files will get reset to None before getting passed to the DNS. It is safer to choose your files with the save option.
                  
                  
