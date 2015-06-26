# -*- coding: utf-8 -*-
#!/usr/bin/env python

######################################
##  This file is responsible to re- ##
## ceive data from ROS environment  ##
## and generate files with information
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
import math
getTime = lambda: int(round(time.time() * 1000))
#### GUI ####
from Tkinter import *
from subprocess import call
from threading import Thread

class Application (Frame):
	def __init__(self, master = None):
		Frame.__init__(self, master)
		self.msg = Label (self, text="Foi detectada uma variacao de posicao consideravel entre o robo real e simulado")
		self.msg.pack()
		self.bye = Button (self, text= "Ok", command= self.quit)
		self.bye.pack()
		self.pack()



global posicoesRobo1
global posicoesRobo3
posicoesRobo1= None
posicoesRobo3= None
listaDistancia = []

#### Posicoes dos robos #####
global robo1
global robo2
global robo3
global robo4
robo1=[]
robo2=[]
robo3=[]
robo4=[]
#############################

def escreverLista (lista, nomeArquivo):
	arquivo = open (nomeArquivo, "w")
	for i in lista:
		arquivo.write (str (i)+ "\n")
	arquivo.close()

def getxy (odom):
	return odom.pose.pose.position.x, odom.pose.pose.position.y#degrees(yall)

import math
def getPos0(w):
	global robo0
	robo0.append(w)

def getPos1(w):
	global robo1
	robo1.append(w)
	global posicoesRobo1
	posicoesRobo1 = w

def getPos2(w):
	global robo2
	robo2.append(w)

def getPos3(w):
	global robo3
	robo3.append(w)
	global posicoesRobo3
	posicoesRobo3 = w

def canCompare():
	global posicoesRobo3
	global posicoesRobo1
	return ((posicoesRobo3 != None ) and (posicoesRobo1 != None))

def criarJanela (entrada):
	app = Application()
	app.master.title("Manager")
	mainloop()


##### Funcoes para fechar os nós respectivos ######
def close1(arg):
	call(["rosnode", "kill" , "/bridge_0"])	
def close2(arg):
	call(["rosnode", "kill" , "/bridge_2"])
def close3 (arg):
	call(["rosnode", "kill" , "/bridge_3"])
##################################################
rospy.init_node("Escuta")
rospy.Subscriber("/robot_0/base_pose_ground_truth",  Odometry, getPos0)
rospy.Subscriber("/robot_1/base_pose_ground_truth",  Odometry, getPos1)
rospy.Subscriber("/robot_2/base_pose_ground_truth",  Odometry, getPos2)
rospy.Subscriber("/robot_3/base_pose_ground_truth",  Odometry, getPos3)

r = rospy.Rate(10) # hz
already = False
try:
	while not rospy.is_shutdown():
		if canCompare():
			global posicoesRobo3
			global posicoesRobo1
			xa, ya = getxy(posicoesRobo1)
			xb, yb = getxy(posicoesRobo3)
			distancia = math.hypot (xa - xb, ya- (yb+5))
#			if (distancia > 1) and (not already):
#				th = Thread (target = criarJanela, args =("", ))
#				t1 = Thread (target = close1, args =("", ))
#				t2 = Thread (target = close2, args =("", ))
#				t3 = Thread (target = close3, args =("", ))
#				th.start()
#				t1.start()
#				t2.start()
#				t3.start()
#				listaDistancia.append(distancia)
#				break
			posicoesRobo1= None
			posicoesRobo2= None
			listaDistancia.append(distancia)
		r.sleep()
except Exception:
	print ("Ocorreu um erro:")
	raise
finally:
	#escrevendo distancia e distancia relativa
	arquivo = open ("./sim/distancia.txt", "w")
	arquivo2= open ("./sim/distanciaRelativa.txt", "w")
	last = 0
	cont = 0
	for i in listaDistancia:
		arquivo.write(str (cont) + ":"+ str (i)+ "\n")
		arquivo2.write(str (cont) + ":"+ str( i - last)+ "\n")
		last = i
		cont =+ 1
	arquivo.close()
	arquivo2.close()
	# escrevendo posicoes	
	escreveLista(robo0, "./sim/posicoesrobo0.txt") 
	escreveLista(robo1, "./sim/posicoesrobo1.txt") 
	escreveLista(robo2, "./sim/posicoesrobo2.txt") 
	escreveLista(robo3, "./sim/posicoesrobo3.txt") 
