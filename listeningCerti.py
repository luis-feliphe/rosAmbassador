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
#####################################################
# This Method responsible to publish data on HLA    #
#####################################################
#Arguments: id, battery , temperature, sensor 1 , sensor 2 , sensor 3 , gps, compass, goto , rotate, activate
def sendData(idrobot ,battery="", temperature="", sensor1="", sensor2="", sensor3="", gps="<0,0>",compass="", goto="", rotate="", activate=""):
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


def getPos(odom_data, numberID):
#Arguments: id, battery , temperature, sensor 1 , sensor 2 , sensor 3 , gps, compass, goto , rotate, activate
#sendData(1, "", "", "", "", "", "<0;0>", "", "", "", "")
	sendData(str(numberID, "", "", "", "", "","<" + str(odom_data.pose.pose.position.x) + ";" + str (odom_data.pose.pose.position.y) + "> " , "", "", "", "")



def getVel2 (Twist):
#Arguments: id, battery , temperature, sensor 1 , sensor 2 , sensor 3 , gps, compass, goto , rotate, activate
	sendData(1, "", "", "", "", "", "<" + str(twist.linearx) + ";" + str (twist.linear.y) + "> "  , "", "", "", "")

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
rospy.Subscriber("robot_0/base_scan", LaserScan, saveScan)

#rospy.Subscriber("cmd_vel_mux/input/teleop",  Twist, getVel2)
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
		###################################
		### Bridge Sending Data to HLA  ###
		##################################
		if dataToSend != None:
			sendData(1, "", "", str(min(dataToSend.ranges)), "", "", "<0;0>", "", "", "", "")
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
	
			if (_goto.count("S")> 0):
				#print "set to stop"
				twist = Twist()
				twist.linear.x = 0
				p.publish (twist)
				walk = False
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
