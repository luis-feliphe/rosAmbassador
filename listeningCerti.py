#!/usr/bin/env python

#####################################################
# This code is responsible by listen events on ROS  #
# and publish on CERTI - HLA.                       #
#####################################################

#ROS 
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random

#CERTI - HLA
import hla.rti
import hla.omt as fom
import struct


################################
#   The  Ambassador class      #
#TODO Move this class to other #
# File                         #
################################
class MyAmbassador(hla.rti.FederateAmbassador):
	def initialize(self):
		#Variables
		self.time = 0
		self.advanceTime = False
		self.isRegistered = False
		self.isAnnounced = False
		self.isReady = False
		self.isConstrained = False
		self.isRegulating = False
		self.posx = None
		self.posy = None
		self.id = None
		#Handles to manipulate data from CERTI - RTIG

		self.classHandle = rtia.getObjectClassHandle("ObjectRoot.robot")
		self.idHandle = rtia.getAttributeHandle("id", self.classHandle)
		self.batteryHandle = rtia.getAttributeHandle("battery", self.classHandle)
		self.temperatureHandle = rtia.getAttributeHandle("temperature", self.classHandle)
		self.sensor1Handle = rtia.getAttributeHandle("sensor1", self.classHandle)
		self.sensor2Handle = rtia.getAttributeHandle("sensor2", self.classHandle)
		self.sensor3Handle = rtia.getAttributeHandle("sensor3", self.classHandle)
		self.gpsHandle = rtia.getAttributeHandle("gps", self.classHandle)
		self.compassHandle = rtia.getAttributeHandle("compass", self.classHandle)
		self.gotoHandle = rtia.getAttributeHandle("goto", self.classHandle)
		self.rotateHandle = rtia.getAttributeHandle("rotate", self.classHandle)
		self.activateHandle = rtia.getAttributeHandle("activate", self.classHandle)
		#Subscribe HLA
		rtia.subscribeObjectClassAttributes(self.classHandle,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		#Publish HLA
		rtia.publishObjectClass(self.classHandle,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		self.myObject = rtia.registerObjectInstance(self.classHandle)#, "ROBO_2")
	###########################
	#Calbacks from CERTI - HLA#
	###########################
	def reflectAttributeValues(self, object, attributes, tag, order, transport, time=None, retraction=None):
		bateria = None
		temperatura = None
		gps = None
		if self.gpsHandle in attributes:
			gps = attributes[self.gpsHandle]
		if self.batteryHandle in attributes:
			bateria = attributes [self.batteryHandle]

		if self.temperatureHandle in attributes:
			valor = attributes[self.temperatureHandle]
			temperatura = valor

		if self.sensor1Handle in attributes:
			pass

	def log (self, valor):
		print ("\033[34m" + valor + "\033[0;0m")


	def terminate(self):
		rtia.deleteObjectInstance(self.myObject, "ROBO_2")

	def startRegistrationForObjectClass(*params):
		print("START", params)

	def provideAttributeValueUpdate(*params):
		print("PROVIDE UAV", params)

	def synchronizationPointRegistrationSucceeded(self, label):
		self.isRegistered = True
		print ("MyAmbassador: Registration Point Succeeded")

	def announceSynchronizationPoint(self, label, tag):
		self.isAnnounced = True
		print ("MyAmbassador: Announce Synchronization Point")

	def federationSynchronized (self,  label):
		self.isReady = True
		print ("MyAmbassador: Ready to run ")

	def timeConstrainedEnabled (self, time):
		self.isConstrained = True

	def timeRegulationEnabled (self, time): 
		self.isRegulating = True

	def discoverObjectInstance(self, object, objectclass, name):
		print("DISCOVER", name)
		rtia.requestObjectAttributeValueUpdate(object,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
	def timeAdvanceGrant (self, time):
		self.advanceTime = True

	########################
	# Methods to Manage    #
	# information from HLA #
	# (not used)           #
	########################
	def getPosx (self):
		if (self.posx == None or self.id == None) : 
			return 0
		return self.posx
	def getId(self):
		if (self.posx == None or self.posy == None) : 
			return 0
		return self.id
	def getPosy (self):
		if (self.posy == None or self.id == None): 
			return 0
		return self.posy
	def setPosx (self, pos):
		print "set x"
		self.posx = pos
	def setPosy (self, pos):
		print "set y"
		self.posy = pos
	def clear (self):
		self.posx = None
		self.posy = None





global mya

##########################################################
# This Method is a callback that is invoqued when ROS    #
# Publish something. Is responsible for send data to HLA.#
##########################################################
def getPos(odom_data, numberID):
	global mya
	mya.id = numberID
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y

	rtia.updateAttributeValues(mya.myObject,
		{mya.idHandle:str(numberID)+" ",
		mya.batteryHandle:"Bateria ",
		mya.temperatureHandle: "temperatura ",
		mya.sensor1Handle:"sensor1 ",
		mya.sensor2Handle:"sensor2 ",
		mya.sensor3Handle:"sensor3 ",
		mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
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
mya.initialize()
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
rospy.init_node('certiListener')

#Topics that this node will subscribe
rospy.Subscriber("robot_0/odom",  Odometry, getPos1)
rospy.Subscriber("robot_1/odom",  Odometry, getPos2)
rospy.Subscriber("robot_2/odom",  Odometry, getPos3)
rospy.Subscriber("robot_3/odom",  Odometry, getPos4)
rospy.Subscriber("robot_4/odom",  Odometry, getPos5)
rospy.Subscriber("robot_5/odom",  Odometry, getPos6)
rospy.Subscriber("robot_6/odom",  Odometry, getPos7)
rospy.Subscriber("robot_7/odom",  Odometry, getPos8)
rospy.Subscriber("robot_8/odom",  Odometry, getPos9)

r = rospy.Rate(2) # hz


################
## Main loop  ##
################
while not rospy.is_shutdown():
	############# HLA ################
	#######  Time Management  ########
	time = rtia.queryFederateTime() + 1
	rtia.timeAdvanceRequest(time)
	print ("Tempo Atual no HLA = " , time)
	print ("Tempo Atual no ROS = ", rospy.Time.now())
	while (mya.advanceTime == False):
		rtia.tick()
	mya.advanceTime = False
	#################################

mya.terminate()
rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)
print("Done.")
