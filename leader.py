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
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
import random
import sys
import time
####
import tf
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
global posicoes
posicoes= {}




def whereImGoing():
	global myId
	global posicoes
	if (myId == "0"): # Im the leader
		return (0, 0)
	elif (myId == "1"):
		if posicoes.has_key(0):
			x, y, z = getxy (posicoes[0])
			return x -1 , y-1
	elif (myId == "2"):
		if posicoes.has_key(0):
			x, y, z = getxy (posicoes[0])
			return x + 1 , y-1
	return 0, 0


def walkon():
	t = Twist()
	t.linear.x = 1
	return t

def walkleft():
	t = Twist()
	t.angular.z = -1
	return t

def walkright():
	t = Twist()
	t.angular.z = 1
	return t
def walkback():
	t = Twist()
	t.linear.x = -1
	return t
def checkObstacle():
	pass

def myPosition():
	global posicoes
	if (posicoes.has_key(int (myId))):
		return getxy(posicoes[int (myId)])
	return 0,0, 0
import math

def isOriented():
	
	x, y = whereImGoing()
	mx, my, mz = myPosition()
	if (not (mx == 0 and my == 0)):
		hip = math.hypot (x - mx, y - my)
		cat = max([x, mx]) - min ([x, mx])
		tmp1 = math.hypot( x -mx, 0 )
		tmp2 = math.hypot( y -my, 0 )
		cat = max ([tmp1, tmp2])
		anguloEsperado = math.degrees(math.cos(float(cat)/hip))
		#print "deslocamento " + str (anguloEsperado) + " cateto " + str (cat) + " hip " + str (hip)
		if mx < x and my <y:
			anguloEsperado += 180
		elif mx < x and my > y:
			anguloEsperado = 180 - anguloEsperado
		elif mx > x and my < y:
			anguloEsperado = 360 - anguloEsperado
		elif mx > x and my > y: 
			anguloEsperado = anguloEsperado
		mz =  mz + 180
		a = max ([anguloEsperado, mz])
		b = min ([anguloEsperado , mz])
		#print "values " + str (anguloEsperado) + " - " + str (mz) + " = " + str (a - b)
		if ((a - b) < 10):
			return True , anguloEsperado, mz
	return False

def ajustOrientation():
	pass

def inPosition():
	x, y = whereImGoing()
	mx, my, mz = myPosition()
	if ((math.hypot(x-mx, y-my))< 1.5):
		return True
	return False

def walk ():
	x, y = whereImGoing()
	mx, my, mz = myPosition()
	myPosition()
	global myId
	if (myId == "0"): # Im the leader
		return walkon()
	elif (myId == "1"):
		if (not inPosition()):
			if (isOriented()):
				print "is oriented"
				return walkon()
			print "is not"
			
			return walkleft()
		else:
			return Twist()
			print "stop"
	elif (myId == "2"):
		return walkright()


def getpos(robotId, odom):
	global posicoes
	posicoes[robotId]= odom

def getPos0(w):
	getpos(0, w)
def getPos1(odom):
	getpos(1, odom)
def getPos2(odom):
	getpos(2, odom)


global last
last = 0
def getxy (odom):
	global last
	teste = [odom.pose.pose.orientation.x, odom.pose.pose.orientation.y, odom.pose.pose.orientation.z, odom.pose.pose.orientation.w]
	euler = tf.transformations.euler_from_quaternion(teste)
	yall = euler[2]
	#print ("Geting orientation")
	#print odom.pose.pose.orientation.z
	#print odom.pose.pose.orientation.w
	if (not (yall == last)):
		temp = (yall * 180)/ 3.14
	#print ("\n")
	last = yall
	#print str (temp) + " "  + str (math.degrees(yall))
	return odom.pose.pose.position.x, odom.pose.pose.position.y, math.degrees(yall)

#############
# ROS SETUP #
#############

#Became a node, using the arg to decide what the number of robot
rospy.init_node('robot_'+str(sys.argv[1]))
global myId
myId = sys.argv[1]

# Publish on cmd_vel Topic
x =  "robot_" + str (sys.argv[1]) + "/cmd_vel"
p = rospy.Publisher(x, Twist)
#subscribing a position of the robot (Not Necessary)
rospy.Subscriber("/robot_0/base_pose_ground_truth",  Odometry, getPos0)
rospy.Subscriber("/robot_1/base_pose_ground_truth",  Odometry, getPos1)
rospy.Subscriber("/robot_2/base_pose_ground_truth",  Odometry, getPos2)

r = rospy.Rate(3) # hz


######################
# control stops ######
######################
rospy.Subscriber("robot_" + str(myId) + "/base_scan", LaserScan, saveScan)

#################
#   Main Loop   #
#################

iteracoes = 0.0
tempoInicial = getTime()
while not rospy.is_shutdown():
	iteracoes += 1
	t = walk()
	p.publish(t)
	r.sleep()
