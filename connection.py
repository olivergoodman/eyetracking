#!/usr/bin/env python

import socket

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

def connect(address, port, buffer_size, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    s.send(message)

    while check_server(address, port):
        data = s.recv(buffer_size)
        print "received data:", data


    s.close()

	# set up separate thread for reading data pts