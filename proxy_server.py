import os, sys, thread, socket

BACKLOG = 50
MAX_DATA_RECV = 4096
DEBUG = False

def main():
	
	host = ''
	port = 8080

	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((host, port))
		s.listen(BACKLOG)

	except socket.error, (value, message):
		if s: 
			s.close()
		print "Could not open socket:", message
		sys.exit(1)

	while 1:
		conn, client_addr = s.accept()
		thread.start_new_thread(proxy_thread, (conn, client_addr))

	s.close()

def proxy_thread(conn, client_addr):
	request = conn.recv(MAX_DATA_RECV)
	first_line = request.split('\n')[0]
	url = first_line.split(' ')[1]

	if(DEBUG):
		print first_line
		print
		print "URL: ", url
		print

	http_pos = url.find("://")
	print "http_pos: ", http_pos
	if(http_pos==-1):
		temp = url

	else:
		temp = url[(http_pos+3):]
		print "temp: ", temp
	
	port_pos = temp.find(":")
	webserver_pos = temp.find("/")
	if webserver_pos == -1:
		webserver_pos = len(temp)

	webserver = ""
	port = -1
	if(port_pos==-1 or webserver_pos < port_pos):
		port = 80
		webserver = temp[:webserver_pos]
	else:
		port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
		webserver = temp[:port_pos]

	print "Connect to:", webserver, port

	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((webserver, port))
		s.send(request)

		while 1:
			data = s.recv(MAX_DATA_RECV)

			if(len(data) > 0):
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
