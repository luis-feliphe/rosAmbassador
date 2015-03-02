#!/usr/bin/env python

#####################################################
# This code is responsible by listen events on ROS  #
# and publish on CERTI - HLA.                       #
#####################################################

#ROS 
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

import random

#CERTI - HLA
from MyAmbassador import MyAmbassador
import hla.rti
import hla.omt as fom
import struct



global mya
global on 
on = True
global cont
cont = 0
##########################################################
# This Method is a callback that is invoqued when ROS    #
# Publish something. Is responsible for send data to HLA.#
##########################################################



def getPos(odom_data, numberID):
	global mya
	#mya.id = numberID
	#pose = odom_data.pose.pose
	#mya.posx = pose.position.x
	#mya.posy = pose.position.y
	#log(" ------------ ")
	#print mya.posx
	#print mya.posy
	#log(" ------------ ")
	rtia.updateAttributeValues(mya.myObject,
		{mya.idHandle:str(numberID)+" ",
		mya.batteryHandle:"Bateria ",
		mya.temperatureHandle: "temperatura ",
		mya.sensor1Handle:"sensor1 ",
		mya.sensor2Handle:"sensor2 ",
		mya.sensor3Handle:"sensor3 ",
		#mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
		mya.gpsHandle: "<" + str(odom_data.pose.pose.position.x) + ";" + str (odom_data.pose.pose.position.y) + "> ",
		mya.compassHandle:"compass ",
		mya.gotoHandle:"goto ",
		mya.rotateHandle:"rotate " ,
		mya.activateHandle:"activate "},
		"update")

def getVel2 (Twist):
	global mya
	#print "testando"
	#velLin = twist.linear.x
	#velAng = twist.angular.y
	rtia.updateAttributeValues(mya.myObject,
		{mya.idHandle:"1 ",
		mya.batteryHandle:"Bateria ",
		mya.temperatureHandle: "temperatura ",
		mya.sensor1Handle:"sensor1 ",
		mya.sensor2Handle:"sensor2 ",
		mya.sensor3Handle:"sensor3 ",
		#mya.gpsHandle: "<" + str(velAng) + ";" + str (velLin) + "> ",
		mya.gpsHandle: "<" + str(twist.linearx) + ";" + str (twist.linear.y) + "> ",
		mya.compassHandle:"compass ",
		mya.gotoHandle:"goto ",
		mya.rotateHandle:"rotate " ,
		mya.activateHandle:"activate "},
		"update")


##############################################
# These methods just invoque the getPos,     #
# too many just beacause is necessary know   #
# from each robot the message is coming      #
##############################################
global dataToSend
dataToSend=None
def saveScan(data):
	global dataToSend
	dataToSend = data
def getPos1(odom_data):
	getPos (odom_data,1)
def getPos2(odom_data):
	getPos(odom_data, 2)
def getPos3(odom_data):
	getPos(odom_data, 3)
def getPos4(odom_data):
	getPos (odom_data,4)
def getPos5(odom_data):
	getPos(odom_data, 5)
def getPos6(odom_data):
	getPos(odom_data, 6)
def getPos7(odom_data):
	getPos(odom_data, 7)
def getPos8(odom_data):
	getPos(odom_data, 8)
def getPos9(odom_data):
	getPos(odom_data, 9)
 
        
def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")



import time

getTime = lambda: int(round(time.time() * 1000))

##########################
### Federation Setup   ###
##########################

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
rtia.joinFederationExecution("uav-recv", "ExampleFederation", mya)
mya.initialize(rtia)
log("inicialized!\n")

# Announce Synchronization Point (not used by Master)
"""   ----
label = "ReadyToRun"
tag =  bytes ("hi!")
rtia.registerFederationSynchronizationPoint(label, tag)
log("Synchronization Point Register!")
while  (mya.isRegistered == False or mya.isAnnounced == False):
	rtia.tick()
print "tick"
--- """

#wait for others federates
x = input ("Waiting for USERS, start aor federations then write a number and press ok.\n")

#Archieve Synchronized Point
while (mya.isAnnounced == False):
        rtia.tick()
rtia.synchronizationPointAchieved("ReadyToRun")


#tia.synchronizationPointAchieved("ReadyToRun")

while (mya.isReady == False):
	rtia.tick()
log ("MyAmbassador : Is Ready to run ")

# Enable Time Policy
currentTime =rtia.queryFederateTime()
lookAhead =1# rtia.queryLookahead()
rtia.enableTimeRegulation(currentTime, lookAhead)
while (mya.isRegulating == False):
	rtia.tick()
rtia.enableTimeConstrained()
while (mya.isConstrained == False):
	rtia.tick()
log("MyAmbassador: Time is Regulating and is Constrained")


#################
#  Setup of ROS #
#################

log ("\t\t------ STARTING ROS SERVICES -------")

# becabe a node
rospy.init_node('bridge')

#Topics that this node will subscribe
#rospy.Subscriber("robot_0/odom",  Odometry, saveData)
#rospy.Subscriber("robot_0/odom",  Odometry, saveData)
rospy.Subscriber("robot_0/base_scan", LaserScan, saveScan)

#rospy.Subscriber("cmd_vel_mux/input/teleop",  Twist, getVel2)
#rospy.Subscriber("robot_2/odom",  Odometry, getPos3)
#rospy.Subscriber("robot_3/odom",  Odometry, getPos4)
#rospy.Subscriber("robot_4/odom",  Odometry, getPos5)
#rospy.Subscriber("robot_5/odom",  Odometry, getPos6)
#rospy.Subscriber("robot_6/odom",  Odometry, getPos7)
#rospy.Subscriber("robot_7/odom",  Odometry, getPos8)
#rospy.Subscriber("robot_8/odom",  Odometry, getPos9)
global p
p = rospy.Publisher("robot_0/cmd_vel", Twist)
global r
r = rospy.Rate(10) # hz

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

tempoInicial = getTime()
try:
	while not rospy.is_shutdown():
		iteracoes+= 1

		####################################
		## Block to get Time ###############
		####################################
		#if aux == 0:
		#	aux = getTime()
		#else:
		#	tmp = getTime()
		#	media.append(tmp-aux)
		#	aux = tmp
		#	print "Tempo medio = " + str(sum(media) /len(media))
		
		###################################
		### Bridge Sending Data to HLA  ###
		##################################
		if dataToSend != None:
			#print "something to send, why? " + str (min(dataToSend.ranges))
			rtia.updateAttributeValues(mya.myObject,
				{mya.idHandle:str(1)+" ",
				mya.batteryHandle:"Bateria ",
				mya.temperatureHandle: "temperatura ",
				mya.sensor1Handle:str(min(dataToSend.ranges))+" ",
				mya.sensor2Handle:"sensor2 ",
				mya.sensor3Handle:"sensor3 ",
				#mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
				mya.gpsHandle: "<" + str(0) + ";" + str (0) + "> ",
				mya.compassHandle:"compass ",
				mya.gotoHandle:"goto ",
				mya.rotateHandle:"rotate " ,
				mya.activateHandle:"activate "},
				"update")
	#		if (sended == False):
	#			befTime = getTime()
	#			print "Here is the before time = " + str( befTime)
	#			sended = True
			dataToSend =  None
			position = None	


		######################################
		### Bridge handling data from  HLA  ##
		######################################
		if mya.hasData==True:
			_goto = mya.attMap["goto"]
			#Walk

			if (_goto.count("W") > 0):
				twist = Twist()
				twist.linear.x = 1
				p.publish (twist)
				#print "Set to walk"
	#			if (received == False):
	#				actualTime = getTime()
	#				print "Tempo de chegada = " + str(actualTime) 
	#				print "Tempo de resposta aproximado = " + str(actualTime-befTime ) 
	#				received = True

			if (_goto.count("S")> 0):
				#print "set to stop"
				twist = Twist()
				twist.linear.x = 0
				p.publish (twist)
				walk = False
	#			if (received == False):
	#				actualTime = getTime()
	#				print "Tempo de chegada = " + str(actualTime) 
	#				print "Tempo de resposta aproximado = " + str(actualTime-befTime ) 
	#				received = True

			#if (walk):
			#	print ("walking")
			#	twist = Twist()
			#	twist.linear.x = 1
			#	p.publish (twist)
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
		r.sleep()
except:	
	print ("finalizando simulacao")
finally:
	tempoFinal = getTime()
	total = tempoFinal - tempoInicial
	print "--------- Ponte -------------"
	print "tempo de simulacao = "+ str(total)
	print "Interacoes = "+ str(iteracoes)
	print "total por loop " + str (total/iteracoes)
mya.terminate()
rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)
print("Done.")
