#!/bin/bash
echo "waiting for a bit .."
sleep 15

echo "resetting wifi"
sudo ifdown wlan0
sudo ifup wlan0

echo "waiting again"
sleep 15

echo "hopefully we have an ip now: "
source /home/robotino/ros/robotino_ws/devel/setup.bash
source /home/robotino/ipconf.sh

sleep 1
xterm -hold -T "node" -display ":0" -e "roslaunch robotino_node robotino_node.launch"&
sleep 1
xterm -hold -T "nav" -display ":0" -e "roslaunch robotino_navigation navigation.launch"&
sleep 10
xterm -hold -T "bridge" -display ":0" -e "roslaunch robotino_node msb_ros_bridge.launch"&
