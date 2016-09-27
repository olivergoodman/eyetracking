#!/usr/bin/env python

import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 6555 #EyeTribe port
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)

    while True:
        try:
            data = s.recv(BUFFER_SIZE)
            print "received data:", data
        except socket.error as e:
            s.close()
            print "Error", e
            raise e