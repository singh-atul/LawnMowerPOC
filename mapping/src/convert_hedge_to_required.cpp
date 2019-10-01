#include "ros/ros.h"
#include "marvelmind_nav/hedge_imu_fusion.h"
#include "marvelmind_nav/hedge_pos_ang.h"
#include "sensor_msgs/Imu.h"
#include "geometry_msgs/PoseWithCovarianceStamped.h"
#include "tf/transform_broadcaster.h"
#include <vector>

class convert_hedge_to_required_node{

    public:

	convert_hedge_to_required_node(){

	imu_fusion_sub_ = nh_.subscribe("hedge_imu_fusion",10,&convert_hedge_to_required_node::imu_fusion_callback, this);
	pos_angle_sub_ = nh_.subscribe("hedge_pos_ang",10,&convert_hedge_to_required_node::pos_ang_callback, this);

	imu_pub_ = nh_.advertise<sensor_msgs::Imu>("required_imu_data", 10, false);
	pose_pub_ = nh_.advertise<geometry_msgs::PoseWithCovarianceStamped>("required_pose_data", 10, false);

	imu_out_.header.frame_id = "beacon_imu_link";
	pose_out_.header.frame_id = "beacon_map";

	init_covariances(nh_);
	}

	void imu_fusion_callback(const marvelmind_nav::hedge_imu_fusion::ConstPtr& imu_fusion_msg){
		
	convert_hedge_to_required_node::imu_out_.header.stamp = ros::Time::now();
	
	convert_hedge_to_required_node::imu_out_.orientation.x = imu_fusion_msg->qx;
	convert_hedge_to_required_node::imu_out_.orientation.y = imu_fusion_msg->qy;
	convert_hedge_to_required_node::imu_out_.orientation.z = imu_fusion_msg->qz;
	convert_hedge_to_required_node::imu_out_.orientation.w = imu_fusion_msg->qw;

	convert_hedge_to_required_node::imu_out_.angular_velocity.x = imu_fusion_msg->vx;
	convert_hedge_to_required_node::imu_out_.angular_velocity.y = imu_fusion_msg->vy;
	convert_hedge_to_required_node::imu_out_.angular_velocity.z = imu_fusion_msg->vz;

	convert_hedge_to_required_node::imu_out_.linear_acceleration.x = imu_fusion_msg->ax;
	convert_hedge_to_required_node::imu_out_.linear_acceleration.y = imu_fusion_msg->ay;
	convert_hedge_to_required_node::imu_out_.linear_acceleration.z = imu_fusion_msg->az;

	convert_hedge_to_required_node::imu_pub_.publish(imu_out_);
	}
	
	void pos_ang_callback(const marvelmind_nav::hedge_pos_ang::ConstPtr& pos_ang_msg){
	
	convert_hedge_to_required_node::pose_out_.header.stamp = ros::Time::now();

	convert_hedge_to_required_node::pose_out_.pose.pose.position.x = pos_ang_msg->x_m;
	convert_hedge_to_required_node::pose_out_.pose.pose.position.y = pos_ang_msg->y_m;
	convert_hedge_to_required_node::pose_out_.pose.pose.position.z = pos_ang_msg->z_m;

	convert_hedge_to_required_node::pose_out_.pose.pose.orientation = tf::createQuaternionMsgFromYaw(pos_ang_msg->angle);

	convert_hedge_to_required_node::pose_pub_.publish(pose_out_);
	}
	
	void init_covariances(ros::NodeHandle &nh_)
	{
		
	std::vector<double> orientation_covar;
	std::vector<double> ang_vel_covar;
	std::vector<double> linear_accel_covar;
	std::vector<double> pose_covar;

	nh_.getParam("imu_orientation_covariance", orientation_covar);
	nh_.getParam("imu_angular_velocity_covariance", ang_vel_covar);
	nh_.getParam("imu_linear_acceleration_covariance", linear_accel_covar);
	nh_.getParam("pose_covariance", pose_covar);

	
	for (int i = 0; i < orientation_covar.size(); i++)
	convert_hedge_to_required_node::imu_out_.orientation_covariance[i] = orientation_covar.at(i);

	for (int i = 0; i < ang_vel_covar.size(); i++)
	convert_hedge_to_required_node::imu_out_.angular_velocity_covariance[i] = ang_vel_covar.at(i);

	for (int i = 0; i < linear_accel_covar.size(); i++)
	convert_hedge_to_required_node::imu_out_.linear_acceleration_covariance[i] = linear_accel_covar.at(i);

	//for (int i = 0; i < pose_covar.size(); i++)
	//convert_hedge_to_required_node::pose_out_.pose.covariance[i] = pose_covar.at(i);
	}
	
    protected:
	ros::NodeHandle nh_;
	//ros::NodeHandle nh_private_("~");

	sensor_msgs::Imu imu_out_;
	geometry_msgs::PoseWithCovarianceStamped pose_out_;

	ros::Subscriber imu_fusion_sub_;
	ros::Subscriber pos_angle_sub_;

	ros::Publisher imu_pub_;
	ros::Publisher pose_pub_;
		
};


int main(int argc, char** argv)
{
    ros::init(argc, argv, "convert_hedge_to_required");
    convert_hedge_to_required_node obj_hedge;
    ros::spin();
    return 0;
}
