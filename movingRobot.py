#!/usr/bin/env python

######################################
# This file simulate a robot on ROS. #
# To use, you need to pass like      #
# argument the numnber of robot,     #
# like "./movingRobot 1"             #
######################################



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
log (" o Starting Ros")

#Became a node, using the arg to decide what the number of robot
rospy.init_node('robot_'+str(sys.argv[1]))

# Publish on cmd_vel Topic
x =  "robot_" + str (sys.argv[1]) + "/cmd_vel"
p = rospy.Publisher(x, Twist)
#subscribing a position of the robot (Not Necessary)
#rospy.Subscriber("odom",  Odometry, getPos)

r = rospy.Rate(10) # hz

global on
on = True
global cont 
cont = 0 
#################
#   Main Loop   #
#################
while not rospy.is_shutdown():
	#print the actual time
	millis = int(round(time.time() * 1000))
	print "tempo no incio do loop " + str(millis)
	# create a twist message with random values
	twist = Twist()
	twist.linear.x = 1
	twist.linear.y = 1
		
	# Publish the message
	p.publish(twist)
	# TODO check if this sleep is necessary
	r.sleep()
