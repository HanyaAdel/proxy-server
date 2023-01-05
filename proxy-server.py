import os
from socket import *
import sys


def isValidURL(url):
    print(url)
    #  os.listdir()
    pathSpecified = os.getcwd()  
    listOfFileNames = os.listdir(pathSpecified)
    print (listOfFileNames)

    f = open("blocked_urls.txt", "rb")
    outputdata = f.readlines()
    for s in outputdata:
        s = s.decode()[:-2] 
        print(s , "\t", url)
        if (s == url): 

            print ("here in isValid")
            return False

    print ("after loop")
    return True
            
            


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
    if str( message, encoding='utf8' ) != '':
        print (message)
        print ("------------------------")

        # Extract the filename from the given message
        print (message.split()[1])
        print ("###############")
        file1 = str( message, encoding='utf8' )
        filename = file1.split()[1].split("/")[1]
        print ("filename: ", filename)
        
        if (not isValidURL(filename)):
            tcpCliSock.send(('HTTP/1.0 200 OK\n').encode('utf-8'))
            tcpCliSock.send(('Content-Type: text/html\n').encode('utf-8'))
            tcpCliSock.send(('\n').encode('utf-8')) # header and body should be separated by additional newline
            tcpCliSock.send(("""
                <html>
                <body>
                <h1>This URL is blocked</h1>
                </body>
                </html>
                 """).encode('utf-8'))

        else:
            fileExist = "false"
            filetouse = "/" + filename
            print ("file to use: ",filetouse)
            try:
            # Check whether the file exist in the cache
                f = open(filetouse[1:], "rb")
                outputdata = f.readlines()
                print("output data: ", outputdata)
                fileExist = "true"

            # ProxyServer finds a cache hit and generates a response message
            
                # tcpCliSock.send(bytes("HTTP/1.0 200 OK\r\n",'utf-8'))
                # tcpCliSock.send(bytes("Content-Type:text/html\r\n",'utf-8'))
            # # Fill in start.
            #     for i in range(0, len(outputdata)):
            #         tcpCliSock.send(outputdata[i])

                resp = ""
                for s in outputdata:
                    resp += s.decode()
                
                tcpCliSock.send(resp.encode())
                
            # Fill in end.
                f.close()
                print ('Read from cache')

        # Error handling for file not found in cache
            except IOError:
                if fileExist == "false":
                # Create a socket on the proxy server
                    c = socket(AF_INET, SOCK_STREAM)
                    hostn = filename.replace("www.", "", 1)
                    print ("host n: ", hostn)
                    try:
                    # Connect to the socket to port 80
                        print("here 1")
                        c.connect((hostn,80))
                        print('Socket connected to port 80 of the host')
                    # fill in start
                    
                    #fill in ends
                
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                        fileobj = c.makefile('rwb')
                        string1 = "GET " + "http://" + filename + " HTTP/1.0\n\n"
                        naming = bytes(string1,'utf-8')
                        c.send(naming)
                        print("here 2")
                        fileobj.write(naming)
                        print("here 3")
                
                    # Read the response into buffer
                        buff = fileobj.readlines() # read all the files to the buffer
                        print("here 4")
                    
                
                    
                    # Create a new file in the cache for the requested file.
                    # Also send the response in the buffer to client socket and the corresponding file in the cache
                        tmpFile = open("./" + filename,"wb")
                        for i in range(0, len(buff)):
                            tmpFile.write(buff[i])
                            tcpCliSock.send(buff[i])
                        print("here 5")
                    # Fill in start.

                    # Fill in end.
                    
                        tmpFile.close()
                    except:
                        print ("Illegal request")
                else:
                # HTTP response message for file not found
                    
                    # Fill in start.
                        print("File not Found")
                    # Fill in end.

        # Close the client and the server sockets
    tcpCliSock.close()
    
# Fill in start.
tcpSerSock.close()
# Fill in end.
    