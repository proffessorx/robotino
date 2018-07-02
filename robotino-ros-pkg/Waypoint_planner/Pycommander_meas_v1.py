#! /usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import PoseWithCovarianceStamped, Quaternion, Pose
from tf.transformations import quaternion_from_euler, euler_from_quaternion
from math import radians, degrees
import time
import os
import os.path

DIR = '/home/robotino/Desktop/Robotino/00_Sig2_Robotino'

YEAR = time.strftime("%Y")
MONTH = time.strftime("%m")
DAY = time.strftime("%d")
HOUR = time.strftime("%H")
MINUTE = time.strftime("%M")
SECOND = time.strftime("%S")

def create_nav_goal(x, y, yaw):
    
    mb_goal = MoveBaseGoal()
    mb_goal.target_pose.header.frame_id = '/map' 
    mb_goal.target_pose.pose.position.x = x
    mb_goal.target_pose.pose.position.y = y
    mb_goal.target_pose.pose.position.z = 0.0 
    angle = radians(yaw) 
    quat = quaternion_from_euler(0.0, 0.0, angle) 
    mb_goal.target_pose.pose.orientation = Quaternion(*quat.tolist())

    return mb_goal

def callback_pose(data):
    
    global a
    global b
    
    x = data.pose.pose.position.x
    y = data.pose.pose.position.y
    roll, pitch, yaw = euler_from_quaternion([data.pose.pose.orientation.x,
                                             data.pose.pose.orientation.y,
                                             data.pose.pose.orientation.z,
                                             data.pose.pose.orientation.w])
    #rospy.loginfo("Current robot pose: x=" + str(x) + "y=" + str(y) + " yaw=" + str(degrees(yaw)) + "º")
 
    a = x
    b = y

print "Messfahrt wird gestartet"
print ""

if __name__=='__main__':
    
    ctr = 0
    wp_pnt = open("waypoints.txt","r")
    #print wp_pnt.read()
    x = []
    y = []
    z = []
    #print wp_pnt[0]
    for line in wp_pnt:
        print "--------------------"
        x1, y1, z1 = line.split(',')
        x.append(x1)
        y.append(y1)
        z.append(z1)
	ctr = ctr + 1
    rospy.init_node("navigation_snippet")
    #clear_costmaps = rospy.ServiceProxy('move_base/clear_costmaps', Empty)
    
    print ""
    for i in range(ctr):
	#print i
        #print x[i]
	#print y[i]
        rospy.Subscriber("/amcl_pose", PoseWithCovarianceStamped, callback_pose)
        nav_as = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        #rospy.loginfo("Connecting to /move_base AS...")
        nav_as.wait_for_server()
        #rospy.loginfo("Connected.")

        #rospy.loginfo("Creating navigation goal...")
        nav_goal = create_nav_goal(float(x[i]), float(y[i]), float(0))
        #rospy.loginfo("Sending goal to x ...")
    	print "Fahrt zu Zielposition:", i
	print "x-Koordinate:", x[i], "y-Koordinate:", y[i]   

        nav_as.send_goal(nav_goal)
        #rospy.loginfo("Waiting for result...")
        nav_as.wait_for_result()
        nav_res = nav_as.get_result()
        nav_state = nav_as.get_state()
        #rospy.loginfo("Done!")
        #print "Result: ", str(nav_res) 
        #print "Nav state: ", str(nav_state)

	print "Ankunft an Zielposition:", i
	print "x-Koordinate:", a, "y-Koordiante:", b
	print ""
	# Signal an Messrechner senden, sodass Messung beginnen kann
	open("/home/robotino/Desktop/Robotino/MessrechnerSim/" + time.strftime("%Y%m%d_%H%M%S") + ".txt", 'w')
	# Anzahl bestimmen
	anzahl_dateien_var = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])	
	time.sleep(1)
	# If Scchleife

	while True:
		
		# Standortdaten speichern
		f = open("/home/robotino/Desktop/Robotino/Standortdaten/" + YEAR + MONTH + DAY + "_" + HOUR + MINUTE + SECOND + "_Messung_V1.txt", 'a+')
		callback_pose		
		f.write(time.strftime("%d") + "." + time.strftime("%m") +"." + time.strftime("%Y") + ";" + time.strftime("%H") + ":" + time.strftime("%M") + ":" + time.strftime("%S") + ";" + str(b) + ";" + str(b) + "\n")
		
		if anzahl_dateien_var == len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]):	
			time.sleep(1)
	
		else:
		
			break 
	
#rospy.loginfo("Done!All points traversed")
print "Alle Zielpositionen erfolgreich angefahren"
