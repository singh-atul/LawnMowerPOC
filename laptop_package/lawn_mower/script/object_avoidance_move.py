#!/usr/bin/env python
#
import rospy ,rospkg
import math
# from geometry_msgs.msg import Twist
#from nav_msgs.msg import Odometry
from sensor_msgs.msg import NavSatFix
import numpy as np
from std_msgs.msg import Float64 ,String
import ast
# from lawn_mower.srv import *
import time
import serial
rospack = rospkg.RosPack()


## --- global varibales
obstacle_flag= False
flag = False
angle = None
s1=None
curr_lat = None
curr_long = None
obj_distance = None
obj_sum = 0
obj_counter = 0 
goalAvoid_flag = False
_pub = None
rate = None

# call back function for compass
def getHeading(data):
    global angle
    angle = data.data

#call back function for GPS
def sendCL(data):
    global curr_lat
    global curr_long
    curr_lat = data.latitude
    curr_long = data.longitude


#call back function for objstacle detected
#act only when "U" is detected , means to take U turn 180 degree turn
def object_detec(data):
    global angle , goalAvoid_flag , obstacle_flag
    print 'data recieved from arduiono is ' , data.data.strip()
    
    if data.data.strip()[0] == 'U':
        
        obstacle_flag= True
        
        goal = angle+180
        if goal> 360 : 
            goal = angle + 180 - 360
        print 'Rotating to avoid obstacle'
        get_desired_heading(goal,3,True)
        goalAvoid_flag =True
        obstacle_flag= False
        
    elif data.data.strip()[0] == 'X':
        obstacle_flag = False



# to send copmmand to controller using command
def sendData(action_data): 
    global _pub , rate

    _pub.publish(action_data)
    rate.sleep()
    # print" data published to topic /controller_cmd" , action_data
   
    
          
#DONE5.1 / 1
def wrap_angle(diff):
    if diff < -180:
        diff +=360
    
    if diff > 180:
        diff -=360
    return diff


#DONE5
def get_desired_heading(goal,heading_threshold = 3,after_stop=False):
    global angle
    print " in get desired headng with current ngle " , angle
    diff = goal - angle
    
    while True: #m
      
        diff = wrap_angle(diff)
        # if diff > 0 :
        #     goal -= 5
        # else:
        #     goal += 5

        if abs(diff) <= heading_threshold:
            print 'Desired direction reached ', goal ,  ' with difference ' , diff
            sendData((str(30)+',S').encode())
            break
        else:
            while abs(diff) > heading_threshold:
                if diff < 0:
                    #print 'Turning Left'
                    if after_stop:
                        sendData((str(37)+',l').encode())
                    else:
                        sendData((str(37)+',L').encode())
                else:
                    #print 'Turning Right'
                    if after_stop:
                        sendData((str(37)+',r').encode())
                    else:
                        sendData((str(37)+',R').encode())
                
                diff = wrap_angle(goal - angle)
                
            
            print 'Final Facing Angle Before Stopiing ',angle
            sendData((str(30)+',S').encode())
            print 'Final Facing Angle After Stopiing ',angle
    
    print 'Desired direction reached ', goal ,  ' with difference ' , diff


#Done4
def distanceToWaypoint(tgt_lat,tgt_long,curr_lat,curr_long):
    delta = math.radians(curr_long - tgt_long)
    sdlong = math.sin(delta)
    cdlong = math.cos(delta)
    lat1 = math.radians(curr_lat)
    lat2 = math.radians(tgt_lat)
    slat1 = math.sin(lat1)
    clat1 = math.cos(lat1)
    slat2 = math.sin(lat2)
    clat2 = math.cos(lat2)
    delta = (clat1 * slat2) - (slat1 * clat2 * cdlong)
    delta = math.pow(delta,2)
    delta += math.pow(clat2 * sdlong,2)
    delta = math.sqrt(delta) 
    denom = (slat1 * slat2) + (clat1 * clat2 * cdlong)
    delta = math.atan2(delta, denom)
    distanceToTarget =  delta * 6372795     #In meters
    return distanceToTarget



#Done3
def course_to_waypoint(tgt_lat,tgt_long,curr_lat,curr_long):
    dlon = math.radians(tgt_long - curr_long)
    cLat = math.radians(curr_lat)
    tLat = math.radians(tgt_lat)
    a1 = math.sin(dlon) * math.cos(tLat)
    a2 = math.sin(cLat) * math.cos(tLat) * math.cos(dlon)
    a2 = math.cos(cLat) * math.sin(tLat) - a2
    a2 = math.atan2(a1, a2)
    targetHeading = math.degrees(a2)
    if targetHeading < 0:
        targetHeading += 360
    return targetHeading


#Done2
def get_next_waypoint(WAYPOINT_INDEX , WAYPOINT_LIST):
    #print 'In waypoint Function'
    print 'Going to fetch waypoint from waypoint list at index, ',WAYPOINT_INDEX
    if WAYPOINT_INDEX>len(WAYPOINT_LIST):
        print 'Allpoints are traversed Going back to station ...'
        sendData((str(0)+',S').encode())
        return [None,None]
    tgt_lat = WAYPOINT_LIST[WAYPOINT_INDEX][0]
    tgt_long= WAYPOINT_LIST[WAYPOINT_INDEX][1]
    return [tgt_lat,tgt_long]


#DONE 1
def getWayPoints():
    WAYPOINT_LIST= []
    abs_path = rospack.get_path("lawn_mower") + "/script/ServerRequestHandler/" + "saved_points_sim.txt"
    with open(abs_path,'r') as pts:
	data = pts.readlines() 
    print data
    for i in data:
        co = ast.literal_eval(i)
        WAYPOINT_LIST.append([co[0],co[1]])
    return WAYPOINT_LIST


#DONE6

 
def move_forward(tgt_lat,tgt_long):
    global curr_lat
    global curr_long
    global obj_distance , obstacle_flag , goalAvoid_flag
    
    dist = distanceToWaypoint(tgt_lat,tgt_long,curr_lat,curr_long)
    # dist = 1.1
    print "Diatance to move based on target points is " , dist
    
    while dist>0.3:    # till distance is 2 m
        
        if not obstacle_flag :
            if goalAvoid_flag :
                
                goalAvoid_flag = False
                print 'Goal is Avoided due to obstacle in path , should move to new point'
                return 
            else :
                ## move as per command
        
                print 'Distance left to cover is ',dist
                if dist > 3.7:
                    # print 'meter : Moving at speed of 30'
                    sendData((str(25)+',F').encode()) #23
                
                elif dist <= 3.7 and dist >= 0.9:
                    # print 'meter : Moving at speed of 20'
                    sendData((str(23)+',F').encode())
                
                elif dist < 0.9:
                    # print 'meter : Moving at speed of 15'
                    sendData((str(24)+',F').encode())
        
        
        else :
            continue

        dist = distanceToWaypoint(tgt_lat,tgt_long,curr_lat,curr_long)
        print 'Calculated the updated distance to move ', dist

    print 'Goal reached  , sending stop command'
    sendData((str(0)+',S').encode())
    return



def pipeline():
    global curr_lat , obstacle_flag , _pub , rate
    global curr_long
    global angle
    
    print 'Going to load datapoints in waypoints list ...'
    WAYPOINT_LIST = getWayPoints()
    print len(WAYPOINT_LIST),' point Loaded in waypoint '
    index = 0
    print 'Execution Started .... '
    while True:
        print 'Fetching goal Coordinates' 
        [tgt_lat,tgt_long] = get_next_waypoint(index,WAYPOINT_LIST)
        if [tgt_lat,tgt_long] == [None, None]:
	        break
        

        if index > 0 and index%2 is 0 : 

            goal = angle+90
            if goal> 360 : 
                goal = angle + 90 - 360
            get_desired_heading(goal,3,True)
            sendData((str(20)+',F').encode())
            rospy.sleep(.5)
            sendData((str(20)+',S').encode())
            
            goal = angle+90
            if goal> 360 : 
                goal = angle + 90 - 360
            get_desired_heading(goal,3,True)
            
            

        elif index > 0 :
            goal = angle-90
            if goal < 0 : 
                goal = 360 + angle - 90 
            get_desired_heading(goal,3,True)
            sendData((str(20)+',F').encode())
            rospy.sleep(.5)
            sendData((str(20)+',S').encode())
            goal = angle-90
            if goal < 0 : 
                goal = 360 + angle - 90 
            get_desired_heading(goal,3,True)
            
        print 'Goal Coordinates Fetched' , [tgt_lat,tgt_long] 
        
        print 'Calling course to waypoint to get the course of waypoints'
        goal = course_to_waypoint(tgt_lat,tgt_long,curr_lat,curr_long)
        print 'Course to waypoint recieved is ',goal , ' degree'
        

        print 'Calling function to calculate distance between current and target coordinates'
        dist = distanceToWaypoint(tgt_lat,tgt_long,curr_lat,curr_long)
        print 'distance to waypoint calculated to be  ',dist , 'meter'
        
        print '------- SUMMARY ---------'
        print 'Current Latitude',curr_lat
        print 'Current Longitude',curr_long
        print 'Target Latitude',tgt_lat
        print 'Target Longitude',tgt_long
        print 'distance to waypoint ',dist , ' meter'
        print 'Course to waypoint recieved is, ',goal , ' degree'
        print '-----------SUMMARY CLOSE----------------'
        

        # print '----ORIENTATION FIXING ------'
        # print 'Fix the orientation by calling the get desired function'
        # print 'Going in get_desired_function' , goal  , ' degree'
        # get_desired_heading(goal,3,False)
        # print 'Out of get_desired function'
        # print 'Difference in angle after running get desired function is ' ,wrap_angle(goal - angle)
        # print ' -  - - ORIENTATION FIXING CLOSE- - - - - - - - - - - '


        # sendData((str(30)+',F').encode())
        # time.sleep(1)
        # sendData((str(30)+',S').encode())
        # print 'Moved Forward'
        # goal = 1
        # get_desired_heading(goal)
        # print 'Turned'
        # sendData((str(30)+',F').encode())
        # time.sleep(1)
        # sendData((str(30)+',S').encode())
        
        print 'Calling function again to get the distance between current and target coordinates as it might have get changed while rotation'
        dist = distanceToWaypoint(tgt_lat,tgt_long,curr_lat,curr_long)
        print 'distance to waypoint calculated to be  ',dist , ' meter'


        print '------ MOVING -----'
        print 'Going to move forward till the tim'
        move_forward(tgt_lat,tgt_long) 
        print 'Out of move_forward function'
        print '- - - - -MOVING CLOSED - - - - - -'
        index +=1
        print '**************************GOING FOR next point at index ',index , 'in waypoint list*********************************'
	
    rospy.signal_shutdown("Code completed")



# def pipeline_test_obstacle():
#     global obstacle_flag , _pub , rate
#     rospy.init_node("controller")
#     time.sleep(1)
#     print 'pipeline_test_obstacle'
    
#     rospy.Subscriber('/controller_cmd_res', String,object_detec,queue_size=1)
#     rospy.Subscriber('/compass_angle', Float64,getHeading,queue_size=1)
#     _pub = rospy.Publisher("/controller_cmd",String,queue_size=1)
#     rate = rospy.Rate(1) # 1hz
#     time.sleep(2)
#     while True:
#         if not obstacle_flag:
#             sendData((str(18)+',F').encode())


if __name__ == '__main__'   :
    
    
    
    ## common publishers and subscribers

    rospy.init_node("startMower")
    rospy.Subscriber('/controller_cmd_res', String,object_detec,queue_size=1)
    rospy.Subscriber('/compass_angle', Float64,getHeading,queue_size=1)
    rospy.Subscriber('/fix', NavSatFix,sendCL)
    _pub = rospy.Publisher("/controller_cmd",String,queue_size=1)
    rate = rospy.Rate(1)
    time.sleep(2)
    print 'Checks'
    #call pipeline function
    while True:
        if curr_lat is not None and curr_long is not None and angle is not None :
            break
    pipeline()

    rospy.spin()
    



'''
The below commented lines are added at 9:28 p.m 23-Oct
'''
# rate = None
# rospy.init_node("controller")
# time.sleep(1)
# print 'pipeline_test_obstacle'
# rospy.Subscriber('/controller_cmd_res', String,object_detec,queue_size=1)    
# rospy.Subscriber('/compass_angle', Float64,getHeading,queue_size=1)
# rospy.Subscriber('/fix', NavSatFix,sendCL)
# _pub = rospy.Publisher("/controller_cmd",String,queue_size=1)
# rate = rospy.Rate(1)
# time.sleep(2)
# pipeline()
# rospy.spin()


# rospy.Subscriber('/compass_angle', Float64,getHeading)
# time.sleep(1)
# rospy.Subscriber('/fix', NavSatFix,sendCL)
# time.sleep(0.1)
# rospy.Subscriber('/sonarData_1', String,object_detec)
# time.sleep(0.1)
# s1=angle
# print 'Current Angle is: ',angle,' degree and its type is ',type(angle)
# print 'Curent Latitude ', curr_lat
# print 'Curent Longitude ', curr_long
# pipeline()
# rospy.spin()
# arduino.close()