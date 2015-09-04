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


VARIACAO_POS = 4
global POSICAO_INICIAL
POSICAO_INICIAL = None

def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")

def scan(var):
	print ("ranges "+ str(min(remove_fromList(var.ranges, 5.0))))

def getxy (odom):
        return round (odom.pose.pose.position.x), round ( odom.pose.pose.position.y)
getTime = lambda: int(round(time.time() * 1000))

global posicao

def getPos0(odom):
	global POSICAO_INICIAL
	if (POSICAO_INICIAL == None):
		x, y = getxy (odom)
		POSICAO_INICIAL  = [x, y]
	global posicao
	posicao = odom 
def posicaoAtual():
	global posicao
	return getxy (posicao)


#############
# ROS SETUP #
#############
log (" o Starting Ros")

#Became a node, using the arg to decide what the number of robot
rospy.init_node('robot_'+str(sys.argv[1]))

# Publish on cmd_vel Topic
x =  "robot_" + str (sys.argv[1]) + "/cmd_vel"
p = rospy.Publisher(x, Twist)
#subscreve na odometria
rospy.Subscriber("/robot_"+ str (sys.argv[1])+"/base_pose_ground_truth",  Odometry, getPos0)

print "inciando como robot"

r = rospy.Rate(freq) # hz
import time
time.sleep (int (sys.argv[2]))
global on
on = True
global cont 
cont = 0 
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
		global POSICAO_INICIAL
		if (POSICAO_INICIAL != None):
			iteracoes+= 1
			x, y  = posicaoAtual()
			# Publish the message
			if (direcao):
				if (x >= POSICAO_INICIAL[0] + VARIACAO_POS ):
					direcao = False
				else:
					twist = Twist()
					twist.linear.x = 0.4
			else:
				if (x < POSICAO_INICIAL[0]):
					direcao = True
				else:
					twist = Twist()
					twist.linear.x = -0.4
			p.publish(twist)
			# TODO check if this sleep is necessary
		r.sleep()
except Exception :
	raise
finally:
	tempoFinal = getTime()
	total = tempoFinal - tempoInicial
	print "--- Obstaculo " + str(sys.argv[1]) + "------------\ntempo de simulacao = "+ str(total) + "\nInteracoes = "+ str(iteracoes) + "\ntotal por loop " + str (total/iteracoes) + "\n\n"
