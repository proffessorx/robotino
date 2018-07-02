#include <ros/ros.h>
#include <std_msgs/String.h>
#include <sstream>
#include <move_base_msgs/MoveBaseAction.h>
#include <actionlib/client/simple_action_client.h>

typedef actionlib::SimpleActionClient<move_base_msgs::MoveBaseAction> MoveBaseClient;

void PublishGoalCallback(const std_msgs::String::ConstPtr& msg)
{
  ROS_INFO("I heard: [%s]", msg->data.c_str());

  //tell the action client that we want to spin a thread by default
  MoveBaseClient ac("move_base", true);

  //wait for the action server to come up
  while(!ac.waitForServer(ros::Duration(5.0))){
    ROS_INFO("Waiting for the move_base action server to come up");
  }

  move_base_msgs::MoveBaseGoal goal;

  //we'll send a goal to the robot to move 1 meter forward
  goal.target_pose.header.frame_id = "map";
  goal.target_pose.header.stamp = ros::Time::now();

  goal.target_pose.pose.position.x = -0.2676; 
  goal.target_pose.pose.position.y = 1.6533;

  goal.target_pose.pose.orientation.w = 0.6876;
  goal.target_pose.pose.orientation.z = 0.726;

  ROS_INFO("Sending goal");
  ac.sendGoal(goal);

  ac.waitForResult();

  if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
    ROS_INFO("Hooray!!!");
  else
    ROS_INFO("The base failed to move for some reason");

}

int main(int argc, char** argv){
  
  ros::init(argc, argv, "PublishGoals");

  ros::NodeHandle n;

  ros::Subscriber sub = n.subscribe("/id", 1000, PublishGoalCallback);
  
  ros::spin();

  return 0;

  }
	

