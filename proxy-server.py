from socket import *


def isValidURL(url):
    #opening the blocked urls file.
    f = open("blocked_urls.txt", "rb")
    outputdata = f.readlines()

    #check whether the url is in the blocked urls
    for s in outputdata:
        s = s.decode()[:-2] 
        if (s == url): 
            return False
        
    return True
            
            
# def renderBlockedPage(tcpCliSock):



# Create a server socket, bind it to a port and start listening
tcpSerPort = 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM) #SOCK_STREAM indicates TCP socket

#bind the server socket and start listening
tcpSerSock.bind(('127.0.0.1', 8888))
tcpSerSock.listen(5)

while True:
    # Start receiving data from the client
    print( 'Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print ('Received a connection from:', addr)
    message = tcpCliSock.recv(2048)
    if len(message) != 0:
        print ("Message received: ", message)
        print ("------------------------")

        # Extract the filename from the given message
        filename = message.split()[1].partition(b"//")[2]
        search = message.split()[1].split(b"//")[1]
        print ("filename: ", filename)
        
        if (not isValidURL(filename)):
            tcpCliSock.send(('HTTP/1.0 200 OK\n').encode('utf-8'))
            tcpCliSock.send(('Content-Type: text/html\n').encode('utf-8'))
            tcpCliSock.send(('\n').encode('utf-8'))
            tcpCliSock.send(("""
                <html>
                <body>
                <h1>This URL is blocked</h1>
                </body>
                </html>
            """).encode('utf-8'))


        else:
            fileExist = "false"
            filetouse = b"/" + filename.replace(b"/",b"")
            print ("file to use: ",filetouse)
            try:
                # Check whether the file exist in the cache
                f = open(filetouse[1:], "rb")
                outputdata = f.readlines()
                print("output data: ", outputdata)
                fileExist = "true"

                # ProxyServer finds a cache hit and generates a response message

                resp = b""
                for s in outputdata:
                    resp += s
                
                tcpCliSock.send(resp)
                
                # Fill in end.
                f.close()
                print ('Read from cache')

            # Error handling for file not found in cache
            except IOError:
                if fileExist == "false":
                # Create a socket on the proxy server
                    c = socket(AF_INET, SOCK_STREAM)
                    hostn = filename.split(b'/')[0].replace(b"www.", b"", 1)
                    print ("host n: ", hostn)
                    try:
                        # Connect to the socket to port 80
                        print("here 1")
                        c.connect((hostn,80))
                        print('Socket connected to port 80 of the host')
                
                        # Create a temporary file on this socket and ask port 80 for the file requested by the client
                        # fileobj = c.makefile('rwb')
                        req = b"GET " + b"http://" + search + b" HTTP/1.0\r\n\r\n"
                        #naming = bytes(string1,'utf-8')
                        c.send(req)
                        print("here 2")
                        # fileobj.write(req.encode())
                        print("here 3")
                
                        # Read the response into buffer
                        # buff = fileobj.readlines() # read all the files to the buffer
                        resp = c.recv(4096)
                        #print("buffer ", resp)
                    
                
                    
                        # Create a new file in the cache for the requested file.
                        # Also send the response in the buffer to client socket and the corresponding file in the cache
                        response = b""
                        while len(resp) > 0:
                            response += resp
                            resp = c.recv(4096)
                        
                        if(filename[-1:] == b'/'):
                            filename = filename[:-1]
                            
                        tmpFile = open(b"./" + filename.replace(b"/",b"") ,"wb")
                        tmpFile.write(response)
                        tmpFile.close()
                        print("here")
                        tcpCliSock.send(response.encode())
                    except:
                        print ("Illegal request")
                else:
                    # HTTP response message for file not found
                    tcpCliSock.send("HTTP/1.0 404 sendErrorErrorError\r\n")                             
                    tcpCliSock.send("Content-Type:text/html\r\n")
                    tcpCliSock.send("\r\n")

    # Close the client and the server sockets
    tcpCliSock.close()
    
    