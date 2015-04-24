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
from tf.transformations import euler_from_quaternion
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


def degrees(value):
	return  math.degrees(value)#((value* 180.0)/math.pi)

def whereImGoing():
	global myId
	global posicoes
	if (myId == "0"): # Im the leader
		return (0, 0)
	elif (myId == "1"):
		if (posicoes.has_key(0)):
			x, y, z = getxy (posicoes[0])
			return x -2 , y-2
	elif (myId == "2"):
		if posicoes.has_key(0):
			x, y, z = getxy (posicoes[0])
			return x + 2 , y-2
	return 0, 0


def walkon():
	t = Twist()
	t.linear.x = 1
	return t

def walkhorario():
	t = Twist()
	t.angular.z = -0.5
	#t.linear.x = 0.2
	return t

def walkantihorario():
	t = Twist()
	t.angular.z = 0.5
	#t.linear.x = 0.2
	return t
def walkback():
	t = Twist()
	t.linear.x = -1
	return t
def checkObstacle():
	pass

def leaderPosition():
	global posicoes
	if (posicoes.has_key(0)):
		return getxy(posicoes[0])
	return 0,0,0
def myPosition():
	global posicoes
	if (posicoes.has_key(int (myId))):
		return getxy(posicoes[int (myId)])
	return 0,0, 0
import math

def isOriented():
	x, y = whereImGoing()
	mx, my, mz = myPosition()
	#print str (mx) + " " + str(my)
	if (not (mx == 0 and my == 0)):
		#calcula a distancia entre meu ponto e o ponto que quero ir
		hip = math.hypot (x - mx, y - my) 
		#cat = max([x, mx]) - min ([x, mx])
		#calcula a distancia dos dois catetos
		tmp1 = math.hypot( x -mx, 0 )
		tmp2 = math.hypot( 0, y -my )
		#seleciona o maior cateto
		cat = max ([tmp1, tmp2])
		#calcula o angulo que preciso estar para
		anguloEsperado = math.degrees(math.cos(float(cat)/hip))
		#print "deslocamento " + str (anguloEsperado) + " cateto " + str (cat) + " hip " + str (hip) + "meu x=" + str (mx) + " meu y=" + str (my)  + " X= " + str (x) + " Y= " + str (y)
		deltax = x - mx
		deltay = y - my
		deltax = abs(deltax)
		deltay = abs(deltay)
		#print "delta y = " + str (deltay)
		#print "delta x = " + str (deltax)
		#print anguloEsperado
		if (deltax<0.19) and y > my:
			anguloEsperado = 90
		elif (deltax<0.19) and y < my:
			anguloEsperado = 270
		elif (deltay<0.19) and mx < x:
			anguloEsperado = 0
		elif (deltay<0.19) and mx > x:
			#print "era pra andar pra esquerda"
			anguloEsperado = 180
		elif mx < x and my <=y:
			pass#anguloEsperado += 180 
		elif mx < x and my >= y:
			anguloEsperado= anguloEsperado +270# = 180 - anguloEsperado
		elif mx > x and my <= y:
			anguloEsperado= anguloEsperado + 90# = 360 - anguloEsperado
		elif mx > x and my >= y: 
			anguloEsperado =anguloEsperado + 180# anguloEsperado
		#mz =  mz + 180
		a = max ([anguloEsperado, mz])
		b = min ([anguloEsperado , mz])
		#print "values " + str (anguloEsperado) + " - " + str (mz) + " = " + str (a - b)
		limin = 3
		if ((a - b) < limin or ((a-b)>(360-limin))):
			return True , anguloEsperado, mz
		return False, anguloEsperado, mz
	return False, 1000, 800



def ajustOrientation():
	lx, ly, lz = leaderPosition()
	mx, my , mz = myPosition()
	if (not (abs(lz - mz)< 4)):
		if (lz > mz ):#Must adjustment
			#print "andar no antihorario"
			return walkantihorario()
		else:
			#print "andar no horario"
			return walkhorario()
	return Twist()

def inPosition():
	x, y = whereImGoing()
	mx, my, mz = myPosition()
	if ((math.hypot(x-mx, y-my))< 0.3):
		return True
	return False

def walk ():
	x, y = whereImGoing()
	mx, my, mz = myPosition()
	myPosition()
	global myId
	if (myId == "0"): # Im the leader
		return walkon()
	else:
		if (not inPosition()):
			orient, ang, mz = isOriented()
			if (orient):
				#print "is oriented"
				return walkon()

			#a = max([ang, mz])
			#b = min([ang, mz])
			#total = ang - mz
			#if (total>180):
			if ((ang - mz) > 0 and (ang-mz) < 180):
				#print "valor que eu quero ir " + str (ang) + " eh maior que o meu " + str (mz)
				#print " anti horario " + str (ang) + " - "  + str (mz) + " = " + str (ang-mz)
				return walkantihorario()
			else:
				#print "valor que eu quero ir " + str (ang) + " eh menor que o meu " + str (mz)
				#print "horario "
				return walkhorario()
		else:
			return Twist()
			#print "stop"


def getpos(robotId, odom):
	global posicoes
	posicoes[robotId]= odom

def getPos0(w):
	getpos(0, w)

def getDegreesFromOdom(w):
	#TODO: HOW CONVERT DATA TO ANGLES
	q = [w.pose.pose.orientation.x,	w.pose.pose.orientation.y, w.pose.pose.orientation.z, w.pose.pose.orientation.w]       
        euler_angles = euler_from_quaternion(q, axes='sxyz')
	current_angle = euler_angles[2]
	if current_angle < 0:
		current_angle = 2 * math.pi + current_angle
	return math.degrees(current_angle)
		
def getPos1(odom):
	getpos(1, odom)
def getPos2(odom):
	getpos(2, odom)


global last
last = 0
def getxy (odom):
	#global last
	#teste = [odom.pose.pose.orientation.x, odom.pose.pose.orientation.y, odom.pose.pose.orientation.z, odom.pose.pose.orientation.w]
	#euler = tf.transformations.euler_from_quaternion(teste)
	#yall = euler[2]
	#print ("Geting orientation")
	#print odom.pose.pose.orientation.z
	#print odom.pose.pose.orientation.w
	#if (not (yall == last)):
	#	temp = (yall * 180)/ 3.14
	#print ("\n")
	#last = yall
	#print str (temp) + " "  + str (math.degrees(yall))
	return odom.pose.pose.position.x, odom.pose.pose.position.y, getDegreesFromOdom (odom)#degrees(yall)

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

r = rospy.Rate(10) # hz


######################
# control stops ######
######################
rospy.Subscriber("robot_" + str(myId) + "/base_scan", LaserScan, saveScan)

#################
#   Main Loop   #
#################



mapaInicio={}
mapaFim= {}




iteracoes = 0.0
tempoInicial = getTime()
try:
	while not rospy.is_shutdown():
		iteracoes += 1
		t = walk()
		p.publish(t)
		r.sleep()
except Exception :
	raise	
	print ("Finalizando simulacao ")
finally:
	tempoFinal = getTime()
	total = tempoFinal - tempoInicial
	print "--------- Ponte -------------"
	print "tempo de simulacao = "+ str(total)
	print "Interacoes = "+ str(iteracoes)
	print "total por loop " + str (total/iteracoes)
	print "----- tempo de mensagens--------"

#
