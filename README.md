#Internet Emulator Version 1.00
--------------------------------

This is the first release of the Internet Emulator. This program is designed to filter DNS requests if set as the primary DNS. You have the ability to filter the DNS queries from a blacklist that redirects all requests specified on the blacklist to the localhost(127.0.0.1). This program also contains an HTTP and HTTPS server with their respective self certified certificates.

The HTTP server is running on the standard http port 80. The HTTPS server is running on the standard HTTPS port 443. The HTTP server supports Virtual hosting by accessing several websites using a single HTTP server. The HTTPS server supports the HTTPS Virtual Hosting equivalent. It does this by checking the name of the host request and passing it to the server so it can load that certificate instead of the default certificate for the HTTPS server.
