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
from sensor_msgs.msg import LaserScan
getTime = lambda: int(round(time.time() * 1000))



def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")

def saveScan(data):
        global dataToSend
        dataToSend = data

global dataToSend
dataToSend=None


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


######################
# control stops ######
######################
rospy.Subscriber("robot_0/base_scan", LaserScan, saveScan)

#################
#   Main Loop   #
#################

iteracoes = 0.0
tempoInicial = getTime()
try:
	while not rospy.is_shutdown():
		iteracoes += 1
		#print the actual time
		#millis = int(round(time.time() * 1000))
		#print "tempo no incio do loop " + str(millis)
		# create a twist message with random values

		#twist.angular.y = -1
		if (dataToSend != None):
			if (float (min(dataToSend.ranges)) > 2):
				twist = Twist()
				print "Valor obtido " + str (min (dataToSend.ranges))
				twist.linear.x= 1
				# Publish the message
				p.publish(twist)
			else:
				print "Nao deveria estar se movendo " 
				twist = Twist()
				print "Valor obtido " + str (min (dataToSend.ranges))
				twist.linear.x= 1
				# Publish the message
				p.publish(twist)
		# TODO check if this sleep is necessary
		r.sleep()
except:
	pass
finally:
        tempoFinal = getTime()
        total = tempoFinal - tempoInicial
        print "------No com inteligencia ---------"
        print "tempo de simulacao = "+ str(total)
        print "Interacoes = "+ str(iteracoes)
        print "total por loop " + str (total/iteracoes)
