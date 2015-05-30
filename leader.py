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

global entrada
global saida
entrada = []
saida = []


global listaPosicoes
listaPosicoes = []
global VEL_MAX #maxima velocidade possivel 
VEL_MAX = 0.8
global dataToSend
dataToSend=None
global posicoes
posicoes= {}
global contpos
contpos = 0
global ultimavelocidade
ultimavelocidade = 0


def degrees(value):
	return (value*180)/math.pi#math.degrees(value)#((value* 180.0)/math.pi)

def whereImGoing():
	global myId
	global posicoes
	if (myId == "0"): # Im the leader
		global contpos
		#return [(10,10),(10,-10) ,(-10,-10) ,(-10,10)][contpos]
		return 10, 10
	elif (myId == "1"):
		if (posicoes.has_key(0)):
			x, y, z = getxy (posicoes[0])
			return x -2 , y-2
	elif (myId == "2"):
		if posicoes.has_key(0):
			x, y, z = getxy (posicoes[0])
			return x + 2 , y-2
	return 0, 0


def calculaVelocidadeLinear(distanciaAlvo):
	global ultimavelocidade
	lastVel = ultimavelocidade
	#Velocidade linear maxima a ser enviada pelo robo 
	MAX_VELOCIDADE_LINEAR= 0.5
	ACELERACAO_LINEAR = 0.05
	velocidadeLinear = 0
	#acelerando ou continua
	if (distanciaAlvo>=4):
		velocidadeLinear = lastVel+ ACELERACAO_LINEAR
		if velocidadeLinear > MAX_VELOCIDADE_LINEAR:
			velocidadeLinear= MAX_VELOCIDADE_LINEAR
		return float(velocidadeLinear)
	#desacelerando
	else:
		velocidadeLinear = velocidadeLinear - ACELERACAO_LINEAR
		if velocidadeLinear < ACELERACAO_LINEAR:
			velocidadeLinear = ACELERACAO_LINEAR
		return float(velocidadeLinear)

def stop():
	return Twist()
def walkon():
	global VEL_MAX
	t = Twist()
	t.linear.x = VEL_MAX #modificado1
	return t

def walkhorario():
	global VEL_MAX
	t = Twist()
	t.angular.z =-VEL_MAX #modificado -0.5
	#t.linear.x = 0.2
	return t

def walkantihorario():
	global VEL_MAX
	t = Twist()
	t.angular.z = VEL_MAX #modificado 0.5
	#t.linear.x = 0.2
	return t


def walkhorarioon(vel):
	global VEL_MAX
	t = Twist()
	t.angular.z = -VEL_MAX #modificado -0.5
#t.linear.x = 0.3# 0.3
	t.linear.x = 0.3#vel# 0.3
	return t

def walkantihorarioon(vel):
	global VEL_MAX
	t = Twist()
	t.angular.z =VEL_MAX # modificado 0.5
	t.linear.x = 0.3
#	t.linear.x = vel# 0.3
	return t


def walkonhorario():
	global VEL_MAX
	t = Twist()
	t.angular.z = -0.3# modificando 1
	t.linear.x = VEL_MAX #1 - modificado
	return t

def walkonantihorario():
	global VEL_MAX
	t = Twist()
	t.angular.z = 0.3 #modificando 1
	t.linear.x = VEL_MAX #modificado 1
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
	if (not (mx == 0 and my == 0)):
		#calcula a distancia entre meu ponto e o ponto que quero ir
		hip = math.hypot (x - mx, y - my) 
		#calcula a distancia dos dois catetos
		tmp1 = math.hypot( x -mx, 0 )
		tmp2 = math.hypot( 0, y -my )
		#seleciona o maior cateto
		cat = max ([tmp1, tmp2])
		#calcula o angulo que preciso estar para
		anguloEsperado = degrees(math.cos(float(cat)/hip))
		#print "deslocamento " + str (anguloEsperado) + " cateto " + str (cat) + " hip " + str (hip) + "meu x=" + str (mx) + " meu y=" + str (my)  + " X= " + str (x) + " Y= " + str (y)
		deltax = x - mx
		deltay = y - my
		deltax = abs(deltax)
		deltay = abs(deltay)
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
		limin =3 
		if ((a - b) < limin or ((a-b)>(360-limin))):
			return True , anguloEsperado, mz, hip
		return False, anguloEsperado, mz, hip
	return False, 1000, 800, 1000



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
		global contpos
		contpos = (contpos + 1)%4
		global ultimavelocidade
		ultimavelocidade = 0
		return True
	return False

def walk ():
	x, y = whereImGoing()
	mx, my, mz = myPosition()
	global entrada
	entrada.append(str (x + 2) +" "+ str(y+ 2) + " "+ str(mx)+" "+ str(my) +" "+ str(mz))
	#myPosition()
	global myId
	if (not inPosition()):
		orient, ang, mz, hip = isOriented()
		#Minimamente orientado
		if (orient):
			#Muito orientado 
			if (int (ang) == int(mz)):
				return walkon()
			#orientado mas necessita de poucos ajustes
			else:
				if ((ang - mz) >= 0 ):
					if ((ang-mz)<180):
						return walkonantihorario()
					else:
						return walkonhorario()
				else:#if ((ang-mz)<0):
					if (abs(ang-mz)<180):
						return walkonhorario()
					else:
						return walkonantihorario()
		#nao esta orientado com distancia curta
		if (hip < 1.5):
			if ((ang - mz) >= 0 ):
				if ((ang-mz)<180):
					return walkantihorario()
				else:
					return walkhorario()
			elif ((ang-mz)<0):
				if (abs(ang-mz)<180):
					return walkhorario()
				else:
					return walkantihorario()
		#Nao esta orientado com distancia maior
		else:
			velocidade = calculaVelocidadeLinear(hip)
			if ((ang - mz) >= 0 ):
				if ((ang-mz)<180):
					return walkantihorarioon(velocidade)
				else:
					return walkhorarioon(velocidade)
			elif ((ang-mz)<0):
				if (abs(ang-mz)<180):
					return walkhorarioon(velocidade)
				else:
					return walkantihorarioon(velocidade)
	return stop()

def getpos(robotId, odom):
	global posicoes
#	if str(myId) == str(robotId):
#		global listaPosicoes
#		x, y , z = getxy(odom)
#		listaPosicoes.append(str (round(x,2)) + ":" + str (round(y, 2)))
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
	return degrees(current_angle)
		
def getPos1(odom):
	getpos(1, odom)
def getPos2(odom):
	getpos(2, odom)


global last
last = 0
def getxy (odom):
	return round (odom.pose.pose.position.x), round ( odom.pose.pose.position.y), round (getDegreesFromOdom (odom))#degrees(yall)

#############
# ROS SETUP #
#############




import socket
print "Starting services, wainting signal from master"
HOST = "192.168.1.6"    # The remote host
PORT = 50000              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall('Hello, world')
data = s.recv(1024)
s.close()
print "starting Application", repr(data)




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
#rospy.Subscriber("/robot_2/base_pose_ground_truth",  Odometry, getPos2)

r = rospy.Rate(6) # 5hz


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
		global ultimavelocidade
		iteracoes += 1
		t = walk()
		ultimavelocidade = t.linear.x
		global saida
		saida.append(": "+ str(t.angular.z) + " " + str(t.linear.x))
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
	global myId
	arquivo = open ("posicoesRobo_"+ str (myId) + ".txt" , "w")
	global entrada
	global saida
	for i in range (0, len (entrada)):
		if (i < len (saida)):
			arquivo.write(entrada[i]+ " " + saida[i]+ "\n")
	arquivo.close()
#
