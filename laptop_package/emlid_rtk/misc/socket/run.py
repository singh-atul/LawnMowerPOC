#!/usr/bin/env python

import socket


TCP_IP = '192.168.2.15'
TCP_PORT = 9001
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!".encode()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
while(True):
    inp = input("Enter msg").encode()
    s.send(inp)
    data = s.recv(BUFFER_SIZE)
    print("received data:", data)

s.close()

#print("received data:", data)
