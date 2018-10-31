#!/usr/bin/env python


#*************************************************************************#
#   Description :                                                         #
#                 Script for moving robot across waypoints using compass  #
#                 and RTK-GPS points                                      #
#   Parameters :                                                          #
#               None                                                      #
#                                                                         #
#**************************V - 1.0****************************************#
#   Date : 08-Oct-2018   By: Gautam  & Atul                               #
#   Initial draft of the script                                           #
#                                                                         #
#**************************V - 2.0****************************************#
#   Date : 24-Oct-2018   By: Gautam  & Atul                               #
#   Basic working code for compass , ultrasonic and RTK-GPS               #
#                                                                         #
#*************************************************************************#


# import required libraries

import rospy ,rospkg # for ROS-Work
import math
import numpy as np
from sensor_msgs.msg import NavSatFix # for RTK-GPS

from std_msgs.msg import Float64 ,String #for other Msgs
import ast # for waypoints file processing
import datetime

rospack = rospkg.RosPack()

class pathFollower:

    def __init__(self):

        self.obstacleFlag= False # for checking if obstacle was deducted
        self.curCompasAngle = None # for storing current compass angle
        self.curLatitude = None # for storing current RTK-GPS latitude value
        self.curLongitude = None # for storing current RTK-GPS longitude value
        
        self.tgtLatitude = None # for storing target RTK-GPS latitude value
        self.tgtLongitude = None # for storing target RTK-GPS longitude value
        self.distanceToTarget = None # for storing diatnce to target location from current location
        self.targetHeading = None # for storing target angle 

        self.goalAvoidFlag = False # for checking is goal is avoided due to obstacle in front
        
        self.controlCmdPub = None # for publishing on topic /controller_cmd 
        self.pubRate = None

        self.WAYPOINT_INDEX = -1
        self.WAYPOINT_LIST = []

        #pwm values for control on road
        self.leftTurnPWM = 37
        self.rightTurnPWM = 37
        self.forwardMaxPWM = 25
        self.forwardMediumPWM = 20
        self.forwardMinPWM = 19 #old 18
        self.stopPWM =0

        #
        self.waypointFilePath = rospack.get_path("lawn_mower") + "/script/ServerRequestHandler/" + "saved_points_sim.txt"

    '''
    call back function for stopping all process
    '''
    def callbackSTOP(self):
        self.publishControlCmd((str(self.stopPWM)+',S').encode())

    '''
    call back function for compass angle recived from topic /compass_angle
    ''' 
    def callbackCompass(self,data):
        self.curCompasAngle = data.data


    '''
    Function to calculate distance between points using latitude and longitude values
    '''
    def calCurrentDistance(self):
        delta = math.radians(self.curLongitude - self.tgtLongitude)
        sdlong = math.sin(delta)
        cdlong = math.cos(delta)
        lat1 = math.radians(self.curLatitude)
        lat2 = math.radians(self.tgtLatitude)
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
        self.distanceToTarget =  delta * 6372795     #In meters
    

    '''
    call back function for GPS data recived from topic /fix
    ''' 
    def callbackGPS(self,data):
        self.curLatitude = data.latitude
        self.curLongitude = data.longitude
        
        #calculate new distance to Target once GPS is updated
        if self.tgtLatitude is not None and self.tgtLongitude is not None :
            self.calCurrentDistance()


    '''
    call back function for data recived from topic /controller_cmd_res
    Act only when "U" or "X" is detected.
    U signifies that obstacle is detected in front and it's not moving , time to 
    move to next waypoint by turning 180 degree
    '''
    
    def callbackControlCmdRes(self,data):
       
        result=data.data.strip()
        print "pathFollower: Info:  " , datetime.datetime.now() , ": callbackControlCmdRes : data recieved is  " , result
        
        # if command recieved is for taking U turn call function to move the robot
        if result[0] == 'U':
            
            self.obstacleFlag = True
            
            goal = self.curCompasAngle+180
            if goal> 360 : 
                goal = self.curCompasAngle + 180 - 360
            
            print "pathFollower: Info:  " , datetime.datetime.now() , ": callbackControlCmdRes : Rotating to goal " , goal , " from current angle " ,self.curCompasAngle
            self.get_desired_heading(goal,2.89,True)
            self.goalAvoidFlag =True
            self.obstacleFlag= False
            
        elif result[0] == 'X':
            self.obstacleFlag = False



    '''
    Function to publish control command on topic /controller_cmd
    '''
    def publishControlCmd(self,action_data): 
        self.controlCmdPub.publish(action_data)
        print "pathFollower: Info:  " , datetime.datetime.now() , ": publishControlCmd : command " , action_data , " published "
        self.pubRate.sleep()
 
    '''
    Function to wrap passed angle with in 360
    '''       
    def wrapAngle(self,angle):
        if angle < -180:
            angle +=360
        
        if angle > 180:
            angle -=360
        
        return angle

    '''
    Function to only do in-place rotation of robot to goal angle from current position
    '''
    def get_desired_heading(self,goal,heading_threshold = 3,after_stop=False):
        
        print "pathFollower: Info:  " , datetime.datetime.now() , ": get_desired_heading : current angle " , self.curCompasAngle
        
        #difference in angle from desired angle
        diffAngle = self.wrapAngle(goal - self.curCompasAngle) #wrap it for movement 

        print "pathFollower: Info:  " , datetime.datetime.now() , ": get_desired_heading : difference in angle " , diffAngle
        while abs(diffAngle) > heading_threshold :
            if diffAngle < 0: #for turning to left side
                
                if after_stop:
                    self.publishControlCmd((str(self.leftTurnPWM)+',l').encode())
                else:
                    self.publishControlCmd((str(self.leftTurnPWM)+',L').encode())
            else: #for turning to right side
                
                if after_stop:
                    self.publishControlCmd((str(self.rightTurnPWM)+',r').encode())
                else:
                    self.publishControlCmd((str(self.rightTurnPWM)+',R').encode())

            diffAngle = self.wrapAngle(goal - self.curCompasAngle)


        self.publishControlCmd((str(self.stopPWM)+',S').encode()) # command to stop AGV
        diffAngle = self.wrapAngle(goal - self.curCompasAngle)
        print "pathFollower: Info:  " , datetime.datetime.now() , ": get_desired_heading : Desired direction ", goal ,  " reached with difference " , diffAngle    
        
    '''
        calculate Target Heading Angle using GPS points
    '''    
    def calTargetHeading(self):
        dlon = math.radians(self.tgtLongitude - self.curLongitude)
        cLat = math.radians(self.curLatitude)
        tLat = math.radians(self.tgtLatitude)
        a1 = math.sin(dlon) * math.cos(tLat)
        a2 = math.sin(cLat) * math.cos(tLat) * math.cos(dlon)
        a2 = math.cos(cLat) * math.sin(tLat) - a2
        a2 = math.atan2(a1, a2)
        self.targetHeading = math.degrees(a2)
        if self.targetHeading < 0:
            self.targetHeading += 360

    '''
        load all waypoints from waypoint file
    '''
    
    def setWaypoints(self):
               
        with open(self.waypointFilePath,'r') as pts:
            rows = pts.readlines() 

        for row in rows:
            co = ast.literal_eval(row)
            self.WAYPOINT_LIST.append([co[0],co[1]])

        print "pathFollower: Info:  " , datetime.datetime.now() , ": setWaypoints :  All Waypoints to Follow " , self.WAYPOINT_LIST
              

    '''
        get new target points for movement
    '''
    
    def getNextWayPoint(self):
        
        self.WAYPOINT_INDEX = self.WAYPOINT_INDEX + 1
        if (self.WAYPOINT_INDEX > len(self.WAYPOINT_LIST)-1 ):
            print "pathFollower: INFO:  " , datetime.datetime.now() , ": getNextWayPoint: Last Waypoint Processed , No More Points to Process , Shutting Down Node " 
            self.publishControlCmd((str(self.stopPWM)+',S').encode()) # command to stop AGV
            rospy.signal_shutdown("Node Completed")
            return False
        
        print "pathFollower: INFO:  " , datetime.datetime.now() , ": getNextWayPoint: Picking waypoint at Index " , self.WAYPOINT_INDEX , " with value as " ,self.WAYPOINT_LIST[self.WAYPOINT_INDEX]
        
        self.tgtLatitude = self.WAYPOINT_LIST[self.WAYPOINT_INDEX][0]
        self.tgtLongitude= self.WAYPOINT_LIST[self.WAYPOINT_INDEX][1]
        rospy.sleep(1)
        
        return True

    '''
        function which will move forward till target is reached
    '''
    def moveStraight(self):

        if self.distanceToTarget is None :
            self.calCurrentDistance()
        
        print "pathFollower: INFO:  " , datetime.datetime.now() , ": moveStraight: Distance to move based on target points is " , self.distanceToTarget
        
        while self.distanceToTarget > 0.25:    # till distance is 2 m
            
            if not self.obstacleFlag :
                if self.goalAvoidFlag :
                    
                    self.goalAvoidFlag = False
                    print "pathFollower: INFO:  " , datetime.datetime.now() , ": moveStraight: Goal is Avoided due to obstacle in path , should move to new point"
                    # call function to set new point
                    return 
                else :
                    ## move as per command
            
                    print "pathFollower: INFO:  " , datetime.datetime.now() , ": moveStraight: Distance left to cover is ", self.distanceToTarget
                    if self.distanceToTarget > 3.7:
                        
                        self.publishControlCmd((str(self.forwardMaxPWM)+',F').encode()) 
                    
                    elif self.distanceToTarget <= 3.7 and self.distanceToTarget >= 0.9:
                        
                        self.publishControlCmd((str(self.forwardMediumPWM)+',F').encode())
                    
                    elif self.distanceToTarget < 0.9:
                        
                        self.publishControlCmd((str(self.forwardMinPWM)+',F').encode())
                        
            else :
                # till object is rotating due to obstacle avoid moving forward
                continue

        self.publishControlCmd((str(self.stopPWM)+',S').encode()) # command to stop AGV
        print "pathFollower: INFO:  " , datetime.datetime.now() , ": moveStraight: Goal reached  , sending stop command"
        
        return

    '''
        Function to take take 90 degree turn to left 
        Move forward for 1 sec
        Turn right again to face towards new point

    '''
    def uTurn(self):
        if self.WAYPOINT_INDEX > 0 and self.WAYPOINT_INDEX%2 is 0 :
            goal = self.curCompasAngle+90
            if goal> 360 :
                goal = self.curCompasAngle + 90 - 360
            
        elif self.WAYPOINT_INDEX > 0:
            goal = self.curCompasAngle-90
            if goal < 0 : 
                goal = 360 + self.curCompasAngle - 90

        self.get_desired_heading(goal,2.95,True)
        self.publishControlCmd((str(self.forwardMediumPWM)+',F').encode())
        rospy.sleep(.5)
        self.publishControlCmd((str(self.stopPWM)+',S').encode())

        if self.WAYPOINT_INDEX > 0 and self.WAYPOINT_INDEX%2 is 0 :
            goal = self.curCompasAngle+90
            if goal> 360 :
                goal = self.curCompasAngle + 90 - 360
            
        elif self.WAYPOINT_INDEX > 0:
            goal = self.curCompasAngle-90
            if goal < 0 : 
                goal = 360 + self.curCompasAngle - 90

        self.get_desired_heading(goal,2.95,True)


    '''
        Pipeline function which call all functions when required to required movement
    '''
    def pipeline(self):
        
        self.setWaypoints()
        moveNextFlag =True
        while moveNextFlag:

            moveNextFlag = self.getNextWayPoint()
            print "pathFollower: INFO: " , datetime.datetime.now() , ": pipeline: Goal Co-Ordinates ", [self.tgtLatitude,self.tgtLongitude]

            
            if self.WAYPOINT_INDEX > 0:
                print "pathFollower: INFO: " , datetime.datetime.now() , ": pipeline: UTurn Function Called , current index value " , self.WAYPOINT_INDEX
                self.uTurn()
           

            print "pathFollower: INFO: " , datetime.datetime.now() , ": pipeline: calling moveStraignt Function with current postion as  " , [self.curLatitude,self.curLongitude]
            self.moveStraight() 
      
        print "pathFollower: INFO: " , datetime.datetime.now() , ": pipeline: All waypoints covered as per process , shutting down the code"
        rospy.signal_shutdown("Code completed")

    '''
        Main function of the class for node initialization and other stuff
    '''
    def main(self):
        rospy.Subscriber('/controller_cmd_res', String,self.callbackControlCmdRes,queue_size=1)
        rospy.Subscriber('/compass_angle', Float64,self.callbackCompass,queue_size=1)
        rospy.Subscriber('/fix', NavSatFix,self.callbackGPS)

        #for stoping processing of AGV further 
        rospy.Subscriber('/stopMower',String,self.callbackSTOP,queue_size=1)

        self.controlCmdPub = rospy.Publisher("/controller_cmd",String,queue_size=1)
        self.pubRate = rospy.Rate(1)

        print "pathFollower: INFO: " , datetime.datetime.now() , ": main: waiting for initial values to be populated for current Latitude & Longitude along with compass angle"
        while True:
            if self.curLatitude is not None and self.curLongitude is not None and self.curCompasAngle is not None :
                break
        self.pipeline()
        rospy.spin()
    


if __name__ == '__main__'   :
    
    rospy.init_node("pathFollower")
    objController = pathFollower()
    objController.main()

    


