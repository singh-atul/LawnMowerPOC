#!/usr/bin/env python

#*************************************************************************#
#   Description :                                                         #
#                 Script for collecting data from sonar sensor            #
#                 and publishing it over a topic for it to be consumed    #
#   Parameters :                                                          #
#                < port Name >                                            #
#                                                                         #
#**************************V - 1.0****************************************#
#   Date : 17-Oct-2018                                                    #
#                                                                         #
#                                                                         #
#*************************************************************************#


import rospy
from std_msgs.msg import String
import serial

# returns 0 if the sensor is not connected
# returns object's distance in the path of the mower if the object is less than the threshold given
# returns -1 otherwise.

def fetch_and_publish(portname):
    # Adding constants
    threshold = 150 # range before which the object detected will be published in cms

    min = 828 
    max = 37630 # max and min values obtained from reading the sensor data which is some arbitrary value.
    
    #sonar_const to get the probability of the value comapred to the maximum range of the sensor and converting distance from inches to cms.
    sonar_const = ( 254 * 2.54 ) / ( max - min ) 
    
    pub = rospy.Publisher('sonarData_1', String, queue_size=5)
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        ser = serial.Serial(port=portname,baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
        data = ser.read_until(" ")
    
	ret = -1
	if len(data.strip()) == 0 :
            data = 0.0
	try:
		if(float(data) == 0 ):
			measurement = 0
		else:
			measurement = (float(data) - min) * sonar_const +17 # added  offset of 17 derived from experimentation
	except :
		print "value of data is " , data ,  " with len" , len(data)
	#print("measurement==",measurement)
	if (measurement < threshold):
		ret = measurement
        pub.publish(str(ret))
        
	rate.sleep()

if __name__ == '__main__':
    try:
        # initialize ros node
        rospy.init_node('sonarDataPublishNode') 
        portname= rospy.get_param('~portname', '/dev/ttyACM0')
        fetch_and_publish(portname)
    except rospy.ROSInterruptException:
	    rospy.loginfo("publish_sonar_data.py : ERROR while publishing sonar data ")
    pass












































A
A
A
A

