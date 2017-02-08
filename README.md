#Internet Emulator Version 1.00
--------------------------------
Contact info:
Ricardo Carretero
higgsbosonseeker@gmail.com
in collaboration with Inho Choi and Eli Schetinsky.

This is the first release of the Internet Emulator. This program is designed to filter DNS requests if set as the primary DNS. This script gives you the ability to filter the DNS queries from a blacklist that redirects all requests specified on the blacklist to the localhost(127.0.0.1). This program also contains an HTTP and HTTPS server with their respective self certified certificates. Written using Python 2.7.12_2.

The program was designed to capture web requests that need to be resolved locally as opposed to letting the browser resolve externally(internet). This allows for the redirection of websites such as www.cnn.com. If the site is listed on the blacklist, the local DNS server will resolve that address to localhost(127.0.0.1) and if the http or https servers are configured correctly, the website is loaded locally and it shows whatever information you choose to serve as an index.html for that website. 

The HTTP server is running on the standard http port 80. The HTTPS server is running on the standard HTTPS port 443. The HTTP server supports Virtual hosting by accessing several websites using a single HTTP server. The HTTPS server supports the HTTPS Virtual Hosting equivalent. It does this by checking the name of the host request and passing it to the server so it can load that certificate instead of the default certificate for the HTTPS server.

How to use:

    Known supported systems: Linux Ubuntu and OSX 
    Untested: Windows systems of any type
    
    Navigate your console to where this program was extracted. If you wish to run the program with the default parameters simply run:
    
    sudo python Main.py
    
 At first your script might not redirect any websites since you will have to add websites to the blacklist. You also have access to a whitelist for more control. The whitelist could be a redirect list or whatever you wish to make of it. The evaluation is as follows:
    Check Black list first
    Check White list
    If site query is not on either lists then access google DNS and obtain the IP.
    
The program will load the following default values: Config.ini for the config files, blacklist.txt for the blacklist, dnsCache.txt for the whitelist, port 53 for the DNS server, port 80 for HTTP, port 443 for HTTPS. You can directly edit the config file to change the load values. The program also supports command line options to specify the following:
 
    [options]:
    
    sudo python Main.py [option]
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


Troubleshooting:

Always make sure that Config.ini has values when loading. While there are some safeguards, it is still recommended to not leave the config file blank.

Port in use error:

If you receive the error [48] socket in use, wait a few minutes before lanching the script again. Also close down any browser tabs you might have open that were loading queries from the script servers.

Root access error:

You will need root access to run the script at the default ports 53, 80, and 443. If you are not authorized for root access then changing the ports to anything above the first 1024 ports will fix that issue. If you switch to any port number besides the standard your browser queries might look like this: http://www.test.com:[port number goes here] or http://www.test.com:5000 same thing goes for HTTPS. https://wwww.test.com:[enter your port here]

DNS server not redirecting to local index file:

Make sure that the DNS server is set at the primary and only DNS server. Also check to make sure that the address you typed in is the desired some such as the difference between http://not.right.com and https://not.right.com. As far as the servers serving the index pages are concerned these are two completely different pages on two completely different servers.

Blacklist.txt warning:

Blacklist.txt is passed to the DNS server as a touple. This allows for faster reading. If you edit the blacklist please add a domain and an IP seperated by a comma. Example:
      1 www.cnn.com., 127.0.0.1
      2 www.foo.com., 127.0.0.1
