#!/bin/bash


sudo killall rosmaster
# start roscore
# echo "roscore executed"
roscore&

# connect to GPS shell and execute the ./demo file
sshpass -p 'emlidreach'  ssh root@rover_rtk './demo'&
#wait for 2 seconds for reach to start
sleep 2

#Start GPS and Compass
roslaunch lawn_mower start_mower_manual.launch&


# #Run pi
sshpass -p 'agv'  ssh agv@agv-desktop 'source ~/poc_v_2/devel/setup.bash;roslaunch lawn_mower agvController.launch'&

#Wait for 5 seconds for pi to estd connection
sleep 5

#Execute run the main code 
roslaunch lawn_mower start_mower.launch&

exit 0