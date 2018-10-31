#!/usr/bin/env python
import rospy
from lawn_mower.srv import *
import serial
import time
from std_msgs.msg import String

arduino = None
_pub=None
def handle_sev_controller_cmd(req):
        global arduino
        try:
            response = "NO"
            while True:
                arduino.flushInput()
                arduino.write(req.control_cmd)
                time.sleep(.5)
                d = arduino.readline()
                if len(d)> 0 :
                    print(d)
                    response="done"
                    break
            
            #     ser.flushInput()
            #     ser.flushOutput()
            #     ser.flush()
            #     ser.write(req.control_cmd)
            #     response = "NO"
            #    # print 'going in while loop'
            #     while True:
            #             print 'In while loop'
            #             time.sleep(.5)
            #             data= ser.readline()
            #             if len(data)>0:
            #                     response="done"
            #                     break

        except Exception as ex :
                print ("controller_aurdino.py : can't connect to aurdino")
                print ex
                response="ERROR"

        return controllerCMDResponse(response)

def controller_cmd_server():
        # global ser
        #rospy.init_node('controller_cmd_server')
        try:
                # ser = serial.Serial('/dev/ttyUSB0',9600,timeout=.1)
                # time.sleep(2)
                # ser.flushInput()
                # ser.flushOutput()
                # ser.flush()
                # print 'connected to arduiono'
                s = rospy.Service('controller_cmd',controllerCMD, handle_sev_controller_cmd)
                print 'service controller_cmd ready for use'
                rospy.spin()
        except:
                print "controller_aurdino.py : can't connect to aurdino"

def callback_control_cmd(data):
        global arduino,_pub
        try:
		print "in callback function"
                while True:
                        arduino.flushInput()
                        arduino.write(data.data)
			print "written to aurdino ",data.data
                        time.sleep(.5)
                        d = arduino.readline()
                        if len(d)> 0 :
                                print ("Command executed ",d)
				_pub.publish(d)
                                break
         

        except Exception as ex :
                print ("controller_aurdino.py : ERROR : can't connect to aurdino , using publisher")
                print ex
        

if __name__ == '__main__':
        rospy.init_node('controller_cmd_server')
        portname= rospy.get_param('~portname', '/dev/ttyUSB0') 
        arduino = serial.Serial(portname, 9600)
        time.sleep(2)
        arduino.flushInput()	
        rospy.Subscriber('/controller_cmd',String,callback_control_cmd,queue_size=1)
	_pub=rospy.Publisher('/controller_cmd_res',String,queue_size=1)        

	print "Script ready to accept data from topic /controller_cmd"
        rospy.spin()
        #arduino.close()
