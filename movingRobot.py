#!/usr/bin/env python

""" Example code of how to move a robot forward for 3 seconds. """

# We always import roslib, and load the manifest to handle dependencies


#Bibliotecas para o ROS 
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random
import sys
import time

#Bibliotecas para o CERTI - HLA
import struct

#Tempo 
from datetime import datetime

######   Methods #######

def getPos(odom_data):
	pose = odom_data.pose.pose
#	print pose.position.x
#	print pose.position.y
	
#	print "\n"
	#rospy.loginfo("Positions %s", data.data)

def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")

###########  CONFIGURACAO E SETUP DO ROS  ###########
log ("\t\t------ STARTING ROS SERVICES -------")

# first thing, init a node!
rospy.init_node('robot_'+str(sys.argv[1]))

# publish to cmd_vel
x =  "robot_" + str (sys.argv[1]) + "/cmd_vel"
p = rospy.Publisher(x, Twist)
#"robot_0/cmd_vel", Twist)
#subscribing a position
rospy.Subscriber("odom",  Odometry, getPos)
r = rospy.Rate(150) # hz



while not rospy.is_shutdown():
	millis = int(round(time.time() * 1000))
	print "tempo no incio do loop " + str(millis)
	################## ROS ####################
	# create a twist message
	twist = Twist()
	twist.linear.x = random.randint(1, 100);
	twist.angular.z = random.randint(1, 100);

	# announce move, and publish the message
	#rospy.loginfo("Enviando a mensagem ")
	p.publish(twist)
	r.sleep()


