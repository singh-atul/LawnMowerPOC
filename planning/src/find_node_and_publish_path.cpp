#include "ros/ros.h"
#include "nav_msgs/Path"
#include <string>
#include "marvelmind_nav/hedge_pos_ang"
#include <dirent.h>

#include 

using namespace std;

std::string file_path = "/home/nvidia/catkin_ws/src/mapping/paths";
float x=-99.99, y=-99.99, yaw=-99.99;
int node_, dest_;

void pose_callback(const marvelmind_nav::hedge_pos_ang::ConstPtr &pose_ang_msg){
	::x = pose_ang_msg->x_m;
	::y = pose_ang_msg->y_m;
	::yaw = pose_ang_msg->yaw;
}

int find_node(){
	std::ifstream file(file_path.c_str());
	std::string str;
	while 
}

int main(int argc, char** argv){

	ros::init(argc, argv, "find_node_and_publish_path");
	ros::NodeHandle nh;
	
	ros::Subscriber pose_sub = nh.subscribe("/hedge_pos_ang", 1, pose_callback);
	
	if not(x==-99.99 && y==-99.99 && yaw==-99.99){
		node_ = find_node();	
	}
	else{
		ROS_ERROR("Pose not initialized.");
		return -1;
	}
		

	ros::Publisher path_pub = 
	
}
