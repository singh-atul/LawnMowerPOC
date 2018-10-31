#!/usr/bin/env python
#Client
import socket


TCP_IP = '127.0.0.1'
TCP_PORT = 5003
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!".encode()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
while(True):
	
	data = s.recv(BUFFER_SIZE)
	print("received data:", data)

s.close()


