#!/usr/bin/env python

""" Example code of how to move a robot forward for 3 seconds. """



#ROS  imports
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random
import sys
import time
####
import struct
from datetime import datetime



def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")

#############
# ROS SETUP #
#############
log ("\t\t------ STARTING ROS SERVICES -------")

#Became a node, using the arg to decide what the number of robot
rospy.init_node('robot_'+str(sys.argv[1]))

# Publish on cmd_vel Topic
x =  "robot_" + str (sys.argv[1]) + "/cmd_vel"
p = rospy.Publisher(x, Twist)
#subscribing a position of the robot (Not Necessary)
#rospy.Subscriber("odom",  Odometry, getPos)

r = rospy.Rate(10) # hz


#################
#   Main Loop   #
#################
while not rospy.is_shutdown():
	#prin the actual time
	millis = int(round(time.time() * 1000))
	print "tempo no incio do loop " + str(millis)
	# create a twist message with random values
	twist = Twist()
	twist.linear.x = random.randint(1, 100);
	twist.angular.z = random.randint(1, 100);
	# Publish the message
	p.publish(twist)
	# TODO check if this sleep is necessary
	r.sleep()
