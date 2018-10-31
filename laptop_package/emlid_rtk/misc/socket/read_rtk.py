#!/usr/bin/env python

import socket


TCP_IP = '192.168.2.15'
TCP_PORT = 9003
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
while(True):
    data = s.recv(BUFFER_SIZE)
    print("received data:", data)

s.close()

#print("received data:", data)
