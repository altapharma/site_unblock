#reference : http://luugiathuy.com/2011/03/simple-web-proxy-python/
import os, sys, thread, socket

BACKLOG = 50  #the number of connections that queue will hold
MAX_DATA_RECV = 4096  #max number of bytes we receive at once
DEBUG = True   #set to True to see the debug messages


#***********************MAIN PROGRAM***********************
def main():
	
	host = ''        #localhost (127.0.0.1)
	port = 8080

	try:
                #create a socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
                #associate the socket to host and port
		s.bind((host, port))

		#listening
		s.listen(BACKLOG)

	except socket.error, (value, message):
		if s: 
			s.close()
		print "Could not open socket:", message
		sys.exit(1)

        #get the connection from client
	while 1:
		conn, client_addr = s.accept()  #accept for client's connection

                #create a thread to handle request
		thread.start_new_thread(proxy_thread, (conn, client_addr))

	s.close()

def proxy_thread(conn, client_addr):

        #get the request from browser
	request = conn.recv(MAX_DATA_RECV)

	#parse the first line
	first_line = request.split('\n')[0]

	#get url
	url = first_line.split(' ')[1]

	if(DEBUG):
		print "first_line: ", first_line  #ex) GET http://test.gilgil.net/ HTTP/1.1
		print
		print "URL: ", url #ex) http://test.gilgil.net
		print

        #find the webserver and port
	http_pos = url.find("://")
	if(http_pos==-1):   #cannot find '://'
		temp = url

	else:
		temp = url[(http_pos+3):]   #after '://' to the end (url) ex) test.gilgil.net/
		print "temp: ", temp
	
	port_pos = temp.find(":")    #find the port position (if any)

	#find end of web server
	webserver_pos = temp.find("/")
	if webserver_pos == -1:
		webserver_pos = len(temp)

	webserver = ""
	port = -1   #just for exception
	if(port_pos==-1 or webserver_pos < port_pos): #there is no port num OR ... cannot understand
		port = 80    #default port
		webserver = temp[:webserver_pos]
	else:   #if there is a port num  [webserver_pos : len(temp)]
 		port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
		webserver = temp[:port_pos]

	print "Connect to:", webserver, "PORT: ", port

	try:
                #create a socket to connect to the web server
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((webserver, port))
		#adding dummpy request
		dummy = 'GET / HTTP/1.1\r\nHost: test.gilgil.net\r\n\r\n'
		request = dummy + request
		s.send(request)  #send request to webserver

		while 1:
                        #receive data from webserver
			data = s.recv(MAX_DATA_RECV)

			if(len(data) > 0):
                                #send to client(browser)
				conn.send(data)
			else:
				break
		s.close()
		conn.close()

	except socket.error, (value, message):
		if s:
			s.close()
		if conn:
			conn.close()
		print "Runtime Error:", message
		sys.exit(1)


if __name__ == '__main__':
	main()
