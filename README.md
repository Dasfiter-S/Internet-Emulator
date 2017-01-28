#Internet Emulator V2.2
-----------------------------------------
HTTPS now working for the socket based server. Still working on servering multiple certificates per port.
#Internet Emulator V2.1
-----------------------------------------
Included sockDev.py which contains a socket server built entirely from the socket library. It is currently being used to construct an HTTP handler and server from the most basic structures.

#Internet Emulator V2
-----------------------------------------
HTTPS sites will be served from the port 443 exclusively. Virtual Hosting is already supported for HTTP on port 80. Deleted most of the Virtual Server code for HTTPS and also removed most of the code that is no longer relevant to maintaining a multiport/server stucture for HTTPS

#Internet Emulator V1.4
-----------------------------------------
View.py has been updated to contain all the handlers. Any type of HTTP or HTTPS handler is now shown through the View file. Updated the DNS server code to inherit from the base server class.

#Internet Emulator V1.3.2
-----------------------------------------
Now checks strings using RegEx for added accuracy. Basic implementation of dynamic pathways is underway. Cleaned up some code that was redundant.

#Internet Emulator V1.3.1
-----------------------------------------
Now supports basic port availability checking. The function availablePorts checks the list free_ports, if empty it returns an open port for the next server. Removed obsolete handlers. All handlers are now inherited from BaseHandler. HandlerFactory is in charge of dispatching the correct handler for specific serverType requests. Working on handling dynamic VS_Host instances that serve a request queue type and then close the server once requests are done.

#Internet Emulator V1.3
-----------------------------------------
Re-factored the OOP design flow of most of the program. More to come. Handlers and Servers for HTTP are inheritable and extendable. 

#Internet Emulator V1.2
-----------------------------------------
Added get_path(self) to Util.py. This new function supports the ability to enter relative paths and then hunts down the absolute path of where the file was executed and combines the result for the absolute path of the specified relative link.

Also now serving HTTPS redirections with their own certificates for cnn.com:8000 and foo.com:8001. Re-wrote part of the host_head() in VSHandler() to enable using the host requested to find the right index file. It is very similar to the host_head() in MyRequestHandler(). 

Created a new handler for the base HTTPS server, RedirectHandler() it will take care of sending HTTPS traffic to the right place. This new handler uses a key pair list and finds the entry requested and returns the redirect or else it sends a not found error.

#Internet Emulator V1.1.3
-----------------------------------------
Fixed a bug that would error out the server when entering the localhost in the browser while the server was running. Also fixed a potential issue where the index file object was being passed off to another function. Now the file is closed after being copied by the view function. Refactored some of the code to streamline the host_head function.

#Internet Emulator V1.1.2
-----------------------------------------
Added factory pattern for server types. Still needs some expanding to support the rest of the servers. Cleaned up some of the commented out lines that were no longer needed for debugging.

#Internet Emulator V1.1
-----------------------------------------
Refactoring code to fit the Model-View-Controller philosophy. Cleaning up code by cutting redundant methods. Renaming variables for clarity and adding comments for easier code parsing. If this project is running on a Vagrant machine make sure that the Vagranfile is is forwarding the following

         config.vm.network "forwarded_port", guest: 80, host: 8080
         config.vm.network "forwarded_port", guest: 443, host: 8443
         config.vm.network "forwarded_port", guest: 53, host: 8053
    
if you are on a mac you can redirect your localhost quieries to the correct ports using

         sudo ipfw add 100 fwd 127.0.0.1,8080 tcp from any to me 80
         sudo ipfw add 101 fwd 127.0.0.1,8443 tcp from any to me 443
         sudo ipfw add 102 fwd 127.0.0.1,8053 tcp from any to me 53

this is important because the Vagrant machine does not have access to ports below port 1024 since it is running headless. Even if you run it as root you will not be able to gain access to those ports. These settings will remain until your machine (not the vagrant one, the host machine) is rebooted.

# Internet Emulator V1
-----------------------------------------
Supports HTTP Virtual hosting
         HTTPS Semi Virtual Hosting
         DNS resolving with options for blacklist and whitefile
         HTTP runs on port 80 by default
         HTTPS run on port 443 by default
         Virtual HTTPS hosts run on port 8000 + n per server
         Supports command line options for:
         
         DNS port
         White file, this option does not work as intended when run without saving
         Black file, this option does not work as intended when run without saving
         HTTP port
         Save option
         HTTPS port
         Config file
