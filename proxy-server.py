from socket import *
from datetime import datetime

#maximum time in seconds
TTL = 1 * 60

def isValidURL(url):
	#opening the blocked urls file.
	f = open("blocked_urls.txt", "rb")
	outputdata = f.readlines()

	#check whether the url is in the blocked urls
	for s in outputdata:
		s = s[:-2] 
		if (s == url): 
			print("not valid")
			return False
		
	return True
			
			
def renderBlockedPage(tcpCliSock):
	tcpCliSock.send(b'HTTP/1.0 200 OK\n')
	tcpCliSock.send(b'Content-Type: text/html\n')
	tcpCliSock.send(b'\n')
	tcpCliSock.send(b"""
		<html>
		<body>
		<h1>This URL is blocked</h1>
		</body>
		</html>
	""")    

def timeExceeded(cachedTime):
	cachedTime = cachedTime[:-2]
	cachedTime = cachedTime.decode()
	cachedTime = datetime.strptime(cachedTime, "%Y-%m-%d %H:%M:%S.f")
	now = datetime.now()
	diff = (now - cachedTime).total_seconds()

	if (diff > TTL):
		return True
	return False


def isValidResponse(response):
	print("response code ",response[9:12])

	if response[9:10]==b'4' or response[9:10]==b'5':
		msg = response[9:].split(b"\r\n")[0]
		return False

	if response[9:12] == b"204":
		return False
	return True


def renderErrorPage():
	tcpCliSock.send(b'HTTP/1.0 200 OK\n')
	tcpCliSock.send(b'Content-Type: text/html\n')
	tcpCliSock.send(b'\n')
	tcpCliSock.send(b"""
		<html>
		<body>
		<h1>The file you asked for is not found</h1>
		</body>
		</html>
	""")  	

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
	print ("Message received: ", message)
	print ("------------------------")

	# Extract the filename from the given message
	filename = message.split()[1].partition(b"//")[2]
	search = message.split()[1].split(b"//")[1]
	print ("filename: ", filename)
	
	if (not isValidURL(filename)):
		renderBlockedPage(tcpCliSock=tcpCliSock)
		continue

	try:
					
		# Check whether the file exist in the cache

		print("Looking for file in cache")

		filetouse = b"/" + filename.replace(b"/",b"")
		f = open(filetouse[1:], "rb")

		# reading the content of the file
		outputdata = f.readlines()

		# Generating a response message
		resp = b""
		for i in range(len(outputdata)):
			if i ==0:
				if (timeExceeded(outputdata[i])):
					print("File in cache is outdated")
					raise IOError
			else:
				resp += outputdata[i]
		
		tcpCliSock.send(resp)

		f.close()
		print("Response retrieved from cache")

	# Error handling for file not found in cache
	except IOError:
		print ("forwarding request to server")

		# Create a socket on the proxy server
		c = socket(AF_INET, SOCK_STREAM)
		hostn = filename.split(b'/')[0].replace(b"www.", b"", 1)

		try:
			# Connect to the socket to port 80
			c.connect((hostn,80))
			print('Socket connected to port 80 of the host')
	
			# ask port 80 for the file requested by the client
			req = b"GET " + b"http://" + search + b" HTTP/1.0\r\n\r\n"
			print("Request: ", req)
			c.send(req)
	
			# Read the response
			resp = c.recv(4096)   


		
			response = b""
			while len(resp) > 0:
				response += resp
				resp = c.recv(4096)
			
			if (not isValidResponse(response=response)):
				raise Exception()
			


			# Create a new file in the cache for the requested file.
			# store the current time along with the data.
			if(filename[-1:] == b'/'):
				filename = filename[:-1]
			tmpFile = open(b"./" + filename.replace(b"/",b"") ,"wb")
			now = datetime.now()
			date_time = now.strftime("%Y-%m-%d %H:%M:%S.f\r\n")
			date_time = date_time.encode()

			tmpFile.write(date_time + response)
			tmpFile.close()
			tcpCliSock.send(response)

			print ("Response retrieved from port 80 and added to cache")
		except:
			renderErrorPage()

	# Close the client and the server sockets
	tcpCliSock.close()