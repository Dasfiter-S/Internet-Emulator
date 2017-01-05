#Internet Emulator V1.2
-----------------------------------------
Added get_path(self) to Util.py. This new function supports the ability to enter relative paths and then hunts down the absolute path of where the file was executed and combines the result for the absolute path of the specified relative link.

Also now serving HTTPS redirections with their own certificates for cnn.com:8000 and foo.com:8001. Re-wrote part of the host_head() in VSHandler() to enable using the host requested to find the right index file. It is very similar to the host_head() in MyRequestHandler(). Still needs some re-writing to get rid of a couple of constants. 

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
