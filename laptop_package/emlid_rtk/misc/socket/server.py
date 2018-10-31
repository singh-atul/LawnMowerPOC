#!/usr/bin/env python

import socket
import random
import time
import sys


data_type = sys.argv[1]

if(data_type == 'nmea'):
	TCP_IP = '127.0.0.1'
	TCP_PORT = 9001
	filename = '/home/infosyssdc3/RTK/Cart_Aug_22/nmea_11_21.txt'
elif(data_type == 'xyz'):
	TCP_IP = '127.0.0.1'
	TCP_PORT = 9002
	filename = '/home/infosyssdc3/RTK/Cart_Aug_22/xyz.txt'
elif(data_type == 'compass'):
	TCP_IP = '127.0.0.1'
	TCP_PORT = 9003
	filename = '/home/infosyssdc3/RTK/Cart_Aug_22/card_compass_data'
else:
	print("Not a valid argument")
	exit()

# TCP_IP = '127.0.0.1'
# TCP_PORT = 9001
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

#filename = '/home/infosyssdc3/RTK/Cart_Aug_22/nmea_11_21.txt'
#filename = '/home/infosyssdc3/RTK/Cart_Aug_22/card_compass_data'
# filename = '/home/infosyssdc3/RTK/Cart_Aug_22/xyz.txt'
file = open(filename,"r")
#line = file.readline().strip()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)
data = 1
err_msg = "nothing"
while 1:
    #data = conn.recv(BUFFER_SIZE)
    # if not data:
    # 	s.listen(1)
    # 	conn, addr = s.accept()
    # 	conn, addr = s.accept()
	#	print('Connection address:', addr)
    #print "received data:", data
    line = file.readline().strip()
    time.sleep(.3)
    #data = random.randint(1,100)
    #err_msg = conn.send(str(data))  # echo
    err_msg = conn.send(line + "\n")
conn.close()

print(err_msg)