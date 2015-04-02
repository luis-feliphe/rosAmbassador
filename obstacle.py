#!/usr/bin/env python

freq = 1500
######################################
# This file simulate a robot on ROS. #
# To use, you need to pass like      #
# argument the numnber of robot,     #
# like "./movingRobot 1"             #
######################################



#ROS  imports
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random
import sys
import time
####
import struct
from datetime import datetime

def remove_fromList(the_list, val):
   return [value for value in the_list if value != val]

def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")

def scan(var):
	print ("ranges "+ str(min(remove_fromList(var.ranges, 5.0))))


global scanner1
scanner1 = None
def esq (data):
	global scanner1
	scanner1 = min(data.ranges)

global scanner2
scanner2 = None
def dire (data):
	global scanner2
	scanner2 = min(data.ranges)

getTime = lambda: int(round(time.time() * 1000))




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
#rospy.Subscriber("/robot_0/base_scan",  LaserScan, scan)
value1 = "robot_" + str(sys.argv[1]) + "/base_scan_0"
value2 = "robot_" + str(sys.argv[1]) + "/base_scan_1"
rospy.Subscriber(value1, LaserScan, esq)
rospy.Subscriber(value2, LaserScan, dire)

print "inciiando como robot"
print value1

r = rospy.Rate(freq) # hz
import time
time.sleep (int (sys.argv[2]))
global on
on = True
global cont 
cont = 0 
#valor padra para testes
#way = 200
way = 500

###################
#Medicao de tempo##
###################
iteracoes = 0.0
tempoInicial = getTime()
#################
#   Main Loop   #
#################
direcao= True
try:
	while not rospy.is_shutdown():
		iteracoes+= 1
		#print the actual time
		millis = int(round(time.time() * 1000))
		#print "tempo no incio do loop " + str(millis)
		# create a twist message with random values
#		if (on):
#			twist = Twist()
#			twist.linear.x = 1
#			twist.linear.y = 1
#			cont = cont +1
#		else:
#			twist = Twist()
#			twist.linear.x = -1
#			twist.linear.y = -1
#			cont = cont+1
#		if (cont > 100000):
#			cont = 0
#			on = not on		
		# Publish the message
		if (direcao):
			if (scanner1<1.5):
				direcao = False
			else:
				twist = Twist()
				twist.linear.x = 1
				twist.linear.y = 1
		else:
			if (scanner2<1.5):
				direcao = True
			else:
				twist = Twist()
				twist.linear.x = -1
				twist.linear.y = -1
		p.publish(twist)
		# TODO check if this sleep is necessary
		r.sleep()
except:
	pass
finally:
        tempoFinal = getTime()
        total = tempoFinal - tempoInicial
        print "--- Obstaculo " + str(sys.argv[1]) + "------------\ntempo de simulacao = "+ str(total) + "\nInteracoes = "+ str(iteracoes) + "\ntotal por loop " + str (total/iteracoes) + "\n\n"

