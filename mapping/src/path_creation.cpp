#include "ros/ros.h"
#include "sensor_msgs/Joy.h"
#include "marvelmind_nav/hedge_pos_ang.h"
#include <iostream>
#include <fstream>
#include <iterator>
#include <vector>
#include <string>

using namespace std;

bool flag = true;
vector<vector<float> > path_vector;

std::string start, end;	
float x, y, yaw; 
vector<float> _temp;


void joy_callback(const sensor_msgs::Joy::ConstPtr &joy_msg){

	if(joy_msg->buttons[3]==1){
		if(::flag==true){
			cout << "Enter starting point : ";
			cin >> ::start;
			cout << "Enter ending point : ";
			cin >> ::end;
			::flag = false;
		}
		else if(::flag==false){
			if(::path_vector.empty())
				ROS_INFO("No path recorded ");
			else{
			   std::string output_file = "/home/nvidia/catkin_ws/src/mapping/paths/"+start+"_"+end+".txt";
			   ofstream myfile(output_file.c_str());			
			   cout << "Path vector size :" << ::path_vector.size();
			   for (int i=0; i< ::path_vector.size(); i++){
				for(int j=0; j< ::path_vector[i].size(); j++){
					myfile << ::path_vector[i][j] << " ";
				}
				myfile << "\n";
			   }
			   ::path_vector.clear();
			   myfile.close(); 
			}
			char continue_;
			cout << "\nContinue recording path (y/n)? ";
			cin >> continue_;
			if(continue_=='y'){
				cout << "Enter starting point : ";
				cin >> ::start;
				cout << "Enter ending point : ";
				cin >> ::end;	
			}
			else if(continue_ == 'n')
				::flag = true;
		}
	}
}

/*
void pose_callback(const geometry_msgs::PoseWithCovarianceStamped::ConstPtr &pose_message){
	::x = pose_message->pose.pose.position.x;
	::y = pose_message->pose.pose.position.y;
	
}

void imu_callback(const sensor_msgs::Imu::ConstPtr &imu_message){
	tf::Quaternion q(
		imu_message->orientation.x,
		imu_message->orientation.y,
		imu_message->orientation.z,
		imu_message->orientation.w );
	tf::Matrix3x3 m(q);
	double roll_, pitch_, yaw_;
	m.getRPY(roll_, pitch_, yaw_);

	::yaw = yaw_;
}
*/

void pose_callback(const marvelmind_nav::hedge_pos_ang::ConstPtr& pos_ang_msg){
	::x = pos_ang_msg->x_m;
	::y = pos_ang_msg->y_m;
	::yaw = pos_ang_msg->angle;
	
	::_temp.push_back(::x);
	::_temp.push_back(::y);
	::_temp.push_back(::yaw);
	::path_vector.push_back(_temp);
	::_temp.clear();
}

int main( int argc, char** argv){

	ROS_INFO("Path creation node started !!!");
	ros::init(argc, argv, "path_creation_node");
	ros::NodeHandle nh_;
	
	ros::Subscriber joy_sub_ = nh_.subscribe("/joy", 10, joy_callback);
	ros::Subscriber pose_sub_ = nh_.subscribe("/hedge_pos_ang", 10, pose_callback);

	ros::spin();
	return 0;
	
}

