#!/usr/bin/env python

import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 6555
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"


def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    print "Attempting to connect to %s on port %s" % (address, port)
    try:
        s.connect((address, port))
        print "Connected to %s on port %s" % (address, port)
        return True
    except socket.error, e:
        print "Connection to %s on port %s failed: %s" % (address, port, e)
        return False

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.send(MESSAGE)

	while check_server(TCP_IP, TCP_PORT):
		data = s.recv(BUFFER_SIZE)
		print "received data:", data

	s.close()

	# set up separate thread for reading data pts