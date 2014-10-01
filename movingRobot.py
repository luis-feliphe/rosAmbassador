#!/usr/bin/env python

""" Example code of how to move a robot forward for 3 seconds. """

# We always import roslib, and load the manifest to handle dependencies

import rospy
#importing messages to be used Twist and Odometry
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random

def getPos(odom_data):
	pose = odom_data.pose.pose
	print pose.position.x
	print pose.position.y
	print "\n"
	#rospy.loginfo("Positions %s", data.data)

# first thing, init a node!
rospy.init_node('move')

# publish to cmd_vel
p = rospy.Publisher("/cmd_vel", Twist)

#rospy.Subscriber("base_pose_ground_truth", String, callback)
rospy.Subscriber("odom",  Odometry, getPos)

r = rospy.Rate(2) # hz


while not rospy.is_shutdown():
	# create a twist message, fill in the details
	twist = Twist()
	twist.linear.x = random.randint(1, 100);
	twist.angular.z = random.randint(1, 100);

	# announce move, and publish the message
	rospy.loginfo("Enviando a mensagem ")
	p.publish(twist)
	r.sleep()

