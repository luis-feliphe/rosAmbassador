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

global mya
global on 
on = True
global cont
cont = 0



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
	#print ("enviando " + str (sensor1) + " "  + str(sensor2)  + " " + str(sensor3)  + " " + str(gps))
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
#	if mya.attMap.has_key("sensor2"):
#		ft = mya.attMap["sensor2"]
#		if (ft.count("none")==0):
#			mapaFim[str(iteracoes)]=float(getTime())
	global dataToSend
	dataToSend = data
#	else:
#		print "Ocorreu um erro, o valor sensor2 nao veio"
#		print (mya.attMap)
#		print "-----------------------------------------\n"


###############################
## Some call backs not used  ##
###############################

#def getPos(odom_data, numberID):
#	sendData(str(numberID, "", "", "", "", "","<" + str(odom_data.pose.pose.position.x) + ";" + str (odom_data.pose.pose.position.y) + "> " , "", "", "", "")

#def getVel2 (Twist):
#	sendData(1, "", "", "", "", "", "<" + str(twist.linearx) + ";" + str (twist.linear.y) + "> "  , "", "", "", "")

#def getPos1(odom_data):
#	getPos (odom_data,1)
       
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
if (mType == "master"):
	isMaster = True
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
	rtia.joinFederationExecution( "ReadyToRun", "ExampleFederation", mya)

mya.initialize(rtia)
log("inicialized!\n")

# Announce Synchronization Point (not used by Master)
if (isMaster==False):
	label = "ReadyToRun"
	#label = "1"
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
#Executando testes distribuidos
rtia.synchronizationPointAchieved("ReadyToRun")
#rtia.synchronizationPointAchieved("1")


#tia.synchronizationPointAchieved("ReadyToRun")

while (mya.isReady == False):
	rtia.tick()
log ("MyAmbassador : Is Ready to run ")

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
	positions["leader"] = [odom.pose.pose.position.x, odom.pose.pose.position.y, odom.pose.pose.orientation.w]
def getPos1(odom):
	global positions
	positions["my"] = [odom.pose.pose.position.x, odom.pose.pose.position.y, getDegreesFromOdom(odom)]

def hasDataToHLA():
	global positions
	return positions.has_key("my") and positions.has_key("leader")

rospy.Subscriber("/robot_0/base_pose_ground_truth",  Odometry, getPos0)
rospy.Subscriber("/robot_" + str (mId) +  "/base_pose_ground_truth",  Odometry, getPos1)
#rospy.Subscriber("/robot_2/base_pose_ground_truth",  Odometry, getPos2)

#rospy.Subscriber("cmd_vel_mux/input/teleop",  Twist, getVel2)
global p
p = rospy.Publisher("robot_" + str(mId)+ "/cmd_vel", Twist)
#global r
#r = rospy.Rate(10) # hz

parada = 0
cont = 0
on = True
walk = False

####### Temporary mechanism to verify response time #######
#sended = False
#received = False
#befTime = None
aux = 0
media = []
################
## Main loop  ##
################
iteracoes = 0.0
### Map para pegar o tempo 


mapaInicio={}
mapaFim= {}




tempoInicial = getTime()
try:
	while not rospy.is_shutdown():
		iteracoes+= 1
		###################################
		### Bridge Sending Data to HLA  ###
		##################################
		if hasDataToHLA():
			global positions
			mapaInicio[str(iteracoes)]=getTime()
			sendData(int (mId), "", "", positions["leader"][0], positions["leader"][1], positions["leader"][2], "<" + str(positions["my"][0])+   ";"  + str(positions["my"][1]) + ";" + str(positions["my"][2])+ ">", "", "", "", "")
			positions = {}
			position = None	


		######################################
		### Bridge handling data from  HLA  ##
		######################################
		if mya.hasData==True:
			_goto = mya.attMap["goto"]
			_tempo = mya.attMap["time"]
			_rid = mya.attMap["id"]
			_iteracoes = mya.attMap["sensor2"]
			mapaFim[str(_iteracoes)]=float (_tempo)
			#print (_rid)
			if (_rid.count(str (mId) ) >0):
				#Walk
				if (_goto.count("none")<1):
					_goto = _goto.replace("\\", "")
					_goto = _goto.replace("\"", "")
					lin, ang = _goto.split(";")
					safe_chars = string.digits + '-'
					ang = ''.join([char if char in safe_chars else '' for char in ang])
					lin = ''.join([char if char in safe_chars else '' for char in lin])
					twist = Twist()
					twist.linear.x = int (lin)
					twist.angular.z = int (ang)
					p.publish (twist)
			mya.hasData = False
			mya.attMap = {}
			

		#######  Time Management  ########
		timeHLA = rtia.queryFederateTime() + 1
		rtia.timeAdvanceRequest(timeHLA)
		#print ("Tempo Atual no HLA = " , timeHLA)
		while (mya.advanceTime == False):
			rtia.tick()
		mya.advanceTime = False
		#################################
	#		_time = int(round(time.time()*1000))
#		r.sleep()
except Exception :
	raise	
	print ("finalizando simulacao")
finally:
	tempoFinal = getTime()
	total = tempoFinal - tempoInicial
	print "--------- Ponte -------------"
	print "tempo de simulacao = "+ str(total)
	print "Interacoes = "+ str(iteracoes)
	print "total por loop " + str (total/iteracoes)
	print "----- tempo de mensagens--------"
	tempo = []
	grafico = {}
	maxvalue = 0
	#print (mapaInicio)
	#print "mapa fim"
	#print (mapaFim)
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

	arquivo = open ("resultadoSimulacao.txt", "w")
	for i in range (0, len (eixoindice)):
		arquivo.write(str (eixoindice[i]) +":"+str(eixovalor[i])+"\n")
	arquivo.close()
#	import numpy 
#	dp = numpy.array(tempo)
#	print ("desvio padrao= "+ str(numpy.std(dp)))
#	print ("media = "+ str(numpy.mean(dp)))
#	import pylab
#	pylab.plot(eixoindice, eixovalor)
#	pylab.xlabel('tempo ms')
#	pylab.ylabel('iteracao')
#	pylab.title('Tempo de resposta ao longo das Iteracoes') 
#	pylab.show()
#	print float(sum(tempo)) / len (tempo)
	
	
mya.terminate()
rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)
print("Done.")
