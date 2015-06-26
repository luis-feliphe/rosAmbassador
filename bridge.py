#!/usr/bin/env python

#####################################################
# This code is responsible by listen events on ROS  #
# and publish on CERTI - HLA.                       #
#####################################################
import sys
#ROS 
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

import random

#CERTI - HLA
from MyAmbassador import MyAmbassador
import hla.rti
import hla.omt as fom
import struct

import string
import math
#other
#from parser import Parser

isMaster=True

global entrada
global saida
entrada = {}
saida={}


global mya
global on 
on = True
global cont
cont = 0
global contadorentrada
contadorentrada = 0
global contadorsaida
contadorsaida = 0


def getDegreesFromOdom(w):
        #TODO: HOW CONVERT DATA TO ANGLES
        q = [w.pose.pose.orientation.x, w.pose.pose.orientation.y, w.pose.pose.orientation.z, w.pose.pose.orientation.w]
        euler_angles = euler_from_quaternion(q, axes='sxyz')
        current_angle = euler_angles[2]
        if current_angle < 0:
                current_angle = 2 * math.pi + current_angle
        return math.degrees(current_angle)




#####################################################
# This Method responsible to publish data on HLA #
#####################################################
#Arguments: id, battery , temperature, sensor 1 , sensor 2 , sensor 3 , gps, compass, goto , rotate, activate
def sendData(idrobot ,battery="", temperature="", sensor1="", sensor2="", sensor3="", gps="<0;0>",compass="", goto="", rotate="", activate=""):
	global mya
	rtia.updateAttributeValues(mya.myObject,
	{mya.idHandle:str(idrobot)+" ",
	mya.batteryHandle:str(battery)+" ",
	mya.temperatureHandle: str(temperature)+" ",
	mya.sensor1Handle:str(sensor1)+" ",
	mya.sensor2Handle:str(sensor2)+" ",
	mya.sensor3Handle:str(sensor3)+" ",
	mya.gpsHandle: str (gps)+" ",
	mya.compassHandle:str(compass)+" ",
	mya.gotoHandle:str(goto)+" ",
	mya.rotateHandle:str(rotate)+" " ,
	mya.activateHandle:str(activate)+" "},
	"update")

###########################
## do not remove yet ###### 
###########################

global dataToSend
dataToSend=None
def saveScan(data):
	global dataToSend
	dataToSend = data
       
def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")


#########################
# function to get time ##
#########################
import time
getTime = lambda: int(round(time.time() * 1000))

##########################
### Federation Setup   ###
##########################



mId, mType =  sys.argv[1], sys.argv[2]
print (mId) 
print (mType)
isLast= False
if (mType == "master"):
	isMaster = True
elif(mType== "last"):
	isMaster= False
	isLast= True
else: 
	isMaster = False




print("Create ambassador")
rtia = hla.rti.RTIAmbassador()
mya = MyAmbassador()

#Create a federation
try:
    rtia.createFederationExecution("ExampleFederation", "PyhlaToPtolemy.fed")
    log("Federation created.\n")
except hla.rti.FederationExecutionAlreadyExists:
    log("Federation already exists.\n")

#join in a federation 
mya = MyAmbassador()
if isMaster:
	rtia.joinFederationExecution("master", "ExampleFederation", mya)
else:
	if (isLast):
		rtia.joinFederationExecution( "ReadyToRun", "ExampleFederation", mya)
	else:
		rtia.joinFederationExecution( str(mId)+"ReadyToRun", "ExampleFederation", mya)

if (mId == "00"):
	mya.initialize(rtia, "1")
elif (mId == "22"):
	mya.initialize(rtia, "2")
elif (mId == "33"):
	mya.initialize(rtia, "3")
else:# (mId == "00"):
	mya.initialize(rtia)
log("inicialized!\n")

# Announce Synchronization Point (not used by Master)
if (isMaster==False):
	#No slave eh pra ser igual ao do la de cima portanto diferente de readyToRun
	if (isLast):
		label = "ReadyToRun"
	else:
		label = str(mId)+ "ReadyToRun"
	tag =  bytes ("hi!")
	rtia.registerFederationSynchronizationPoint(label, tag)
	log("Synchronization Point Register!")
	while  (mya.isRegistered == False or mya.isAnnounced == False):
		rtia.tick()
	print "tick"

#wait for others federates
x = input ("Waiting for USERS, start aor federations then write a number and press ok.\n")

#Archieve Synchronized Point

while (mya.isAnnounced == False):
        rtia.tick()

log("Calling Archieve Synchronized Point: Ready TO Run, waiting for federation\n")
#Executando testes distribuidos
rtia.synchronizationPointAchieved("ReadyToRun")
#rtia.synchronizationPointAchieved("22")


#tia.synchronizationPointAchieved("ReadyToRun")

while (mya.isReady == False):
	rtia.tick()

# Enable Time Policy
currentTime =rtia.queryFederateTime()
lookAhead =1# rtia.queryLookahead()
### C OMENTANDO PARA VERIFICAR TEMPO #####################
rtia.enableTimeRegulation(currentTime, lookAhead)
while (mya.isRegulating == False):
	rtia.tick()
rtia.enableTimeConstrained()
while (mya.isConstrained == False):
	rtia.tick()
##########################################################
log("MyAmbassador: Time is Regulating and is Constrained")


#################
#  Setup of ROS #
#################

global listaPosicoes
listaPosicoes= []

log ("\t\t------ STARTING ROS SERVICES -------")

# becabe a node
rospy.init_node('bridge_'+ str (mId))

#Topics that this node will subscribe
#rospy.Subscriber("robot_0/odom",  Odometry, saveData)
#rospy.Subscriber("robot_0/base_scan", LaserScan, saveScan)

global positions
positions = {}
def getPos0(odom):
	global positions
	positions["leader"] = [round (odom.pose.pose.position.x), round (odom.pose.pose.position.y), round (odom.pose.pose.orientation.w)]
def getPos1(odom):
	global positions
	global listaPosicoes
	positions["my"] = [round (odom.pose.pose.position.x), round (odom.pose.pose.position.y), round (getDegreesFromOdom(odom))]
	listaPosicoes.append(str(round(odom.pose.pose.position.x, 2)) + ":"+ str (round(odom.pose.pose.position.y, 2)))
def hasDataToHLA():
	global positions
	return positions.has_key("my") and positions.has_key("leader")

rospy.Subscriber("/robot_0/base_pose_ground_truth",  Odometry, getPos0)
rospy.Subscriber("/robot_" + str (mId[0]) +  "/base_pose_ground_truth",  Odometry, getPos1)
#rospy.Subscriber("/robot_2/base_pose_ground_truth",  Odometry, getPos2)

#rospy.Subscriber("cmd_vel_mux/input/teleop",  Twist, getVel2)
global p
p = rospy.Publisher("robot_" + str(mId[0])+ "/cmd_vel", Twist)
#global r
r = rospy.Rate(30)# hz

parada = 0
cont = 0
on = True
walk = False

aux = 0
media = []

global IteracoesROS
IteracoesROS = 1







################
## Main loop  ##
################
iteracoes = 0.0
### Map para pegar o tempo 

global mapaInicio
mapaInicio={}
global mapaFim
mapaFim= {}


global newConter
newConter = 0





from threading import Thread
def rosLoop (oi):
	while not rospy.is_shutdown():
		global IteracoesROS

		###################################
		### Bridge Sending Data to HLA  ###
		##################################
		if hasDataToHLA():
			global newConter
			newConter+= 1
			global positions
			#mapaInicio[str(iteracoes)]=getTime()
			global mapaInicio
			mapaInicio[str(newConter)]=getTime()
			#Adicionando ao log: leaderX, leaderY, leaderZ, posX, posY, posZ 
			global entrada
			global contadorentrada
			global mId
			sendData(mId, "", "", positions["leader"][0], positions["leader"][1], positions["leader"][2], "<" + str(positions["my"][0])+   ";"  + str(positions["my"][1]) + ";" + str(positions["my"][2])+ ">", "", "", "", str ( newConter ))
			#positions = {}
			#position = None	

		r.sleep()
		IteracoesROS += 1








#if isMaster:
#	print "Im waiting the client request"
#	import socket
#	HOST = ""
#	PORT = 50000
#	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#	s.bind((HOST, PORT))
#	s.listen(1)
#	conn, addr = s.accept()
#	print "Starting The ROBOT"
#	while 1:
#		data = conn.recv(1024)
#		if not data:break
#		conn.sendall(data)
#	conn.close()
	

tempoInicial = getTime()
th= Thread(target= rosLoop, args= ("", ))
th.start()

try:
	while not rospy.is_shutdown():
		iteracoes+= 1




		######################################
		### Bridge handling data from  HLA  ##
		######################################
		if mya.hasData():
			evento = mya.getData()
			_goto = evento["goto"]
			_tempo =evento["time"]
			_rid = evento["id"]
			_iteracoes = evento["activate"]
			_iteracoes= _iteracoes.replace("\\", "").replace("\"", "").replace(";", "").replace(" ", "").replace("\x00", "")

			if (_rid.count(str (mId[0]) ) >0):
				#Walk
				if (_goto.count("none")<1 and _goto.count(";")== 1):
					global mapaFim
					mapaFim[str(_iteracoes)]=float (_tempo)

					_goto = _goto.replace("\\", "")
					_goto = _goto.replace("\"", "")
					lin, ang = _goto.split(";")
					#print ("Linear: " + str (lin) + " angular: "+ str (ang)+ "(Before)" )
					safe_chars = string.digits + '-.'
					ang = ''.join([char if char in safe_chars else '' for char in ang])
					lin = ''.join([char if char in safe_chars else '' for char in lin])
					twist = Twist()
					#print ("Linear: " + str (float (lin)) + " angular: "+ str (float (ang)) )
					global saida
					global contadorsaida
					saida[contadorsaida] = str (ang) + " " + str (lin)
					contadorsaida += 1
					twist.linear.x = round (float (lin), 2)
					twist.angular.z = round (float (ang), 2)
					p.publish (twist)

		#######  Time Management  ########
		timeHLA = rtia.queryFederateTime() + 1
		rtia.timeAdvanceRequest(timeHLA)
		#print ("Tempo Atual no HLA = " , timeHLA)
		while (mya.advanceTime == False):
			rtia.tick()
		mya.advanceTime = False
		#################################
	#		_time = int(round(time.time()*1000))
		#r.sleep()
except Exception :
	print ("finalizando simulacao")
	raise	

finally:
	tempoFinal = getTime()
	total = tempoFinal - tempoInicial
	print "--------- LOOP HLA -------------"
	print "tempo de simulacao = "+ str(total)
	print "Interacoes = "+ str(iteracoes)
	print "total por loop " + str (total/iteracoes)
	print "--------- LOOP ROS -------------"
	print "Interacoes  = "+ str(IteracoesROS)
	print "total por loop " + str (total/float(IteracoesROS))
	print "--------------------------------"
	tempo = []
	grafico = {}
	maxvalue = 0
	global mapaInicio
	global mapaFim
	for i in mapaInicio.iterkeys():
		if (mapaFim.has_key(i)):
			valuetmp = mapaFim[i]-mapaInicio[i]
			tempo.append(valuetmp)
			grafico[float (i)] = valuetmp
			if float (i)> maxvalue:
				maxvalue = float (i) 
	eixoindice = []
	eixovalor = []
	for i in range (0, int(maxvalue)):
		if grafico.has_key(i):
			eixoindice.append(int(i))
			eixovalor.append(int(grafico[float (i)]))

	arquivo = open ("./sim/Simulacao_Robo_"+str (mId) + ".txt", "w")
	for i in range (0, len (eixoindice)):
		arquivo.write(str (eixoindice[i]) +":"+str(eixovalor[i])+"\n")
	arquivo.close()

	####Log system#####
	global entrada
	global saida
	log = open ("./sim/logsimulacao"+ str (mId)+".txt", "w")
	for i in entrada.iterkeys():
		if (saida.has_key(i)):
			log.write(entrada[i] + " : " + saida[i]+ "\n")
	log.close()
			

	
mya.terminate()
rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)
print("Done.")
