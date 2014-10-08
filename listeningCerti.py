#!/usr/bin/env python


#Bibliotecas para o ROS 
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random

#Bibliotecas para o CERTI - HLA
import hla.rti
import hla.omt as fom
import struct

#Classe utilizada pelo CERTI


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
		######## Configurando objetos a serem recebidos ##############

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

		rtia.subscribeObjectClassAttributes(self.classHandle,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		##############################################################
		rtia.publishObjectClass(self.classHandle,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		self.myObject = rtia.registerObjectInstance(self.classHandle)#, "ROBO_2")

	def reflectAttributeValues(self, object, attributes, tag, order, transport, time=None, retraction=None):
		bateria = None
		temperatura = None
		gps = None
		if self.gpsHandle in attributes:
			gps = attributes[self.gpsHandle]
		if self.batteryHandle in attributes:
			bateria = attributes [self.batteryHandle]
			#print("REFLECT", attributes[self.batteryHandle])
			#print("Alguma coisa nao esta certa aqui")
			#pass

		if self.temperatureHandle in attributes:
			#print("REFLECT", attributes[self.temperatureHandle])
			valor = attributes[self.temperatureHandle]
			temperatura = valor
			"""valor =  valor.split(":")[1]
			valor =  valor.replace("\"", "")
			valor =  valor.replace("\\", "")
			valor =  valor.replace(">", "")
			valor =  valor.replace("<", "")
			x, y  = valor.split(";")
			import time
			time.sleep(1)
			print ("valor x : " + str (x) + " valor y : " + str (y))"""
			#print ("Received value: ", valor)
			#if (int (x) != 0):
				#TODO Do something
				#self.ser.write("<"+ str(x)+ ":" + str( y )+ ">")
				#print ("dados enviados ao Arduino")
				#pass


		if self.sensor1Handle in attributes:
			#print("REFLECT", attributes[self.sensor1Handle])
			pass#print("REFLECT", attributes[self.sensor1Handle])
#		self.log("Valores: Bateria: " +str (bateria) + "; Temperatura: " + str(temperatura) + "; GPS: " + str (gps))

	def log (self, valor):
		print ("\033[34m" + valor + "\033[0;0m")


	def terminate(self):
		rtia.deleteObjectInstance(self.myObject, "ROBO_2")

	# RTI callbacks
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

	#### Methods to manage information with HLA #####
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

######   Methods #######

def getPos(odom_data):
	print "dados do robot 1"
	global mya
	mya.id = 1
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y
	#print pose.position.x
	#print pose.position.y

	rtia.updateAttributeValues(mya.myObject,
		{mya.idHandle:"1 ",
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
        #rtia.tick() #1.0, 1.0)




	
	#rospy.loginfo("Positions %s", data.data)

def getPos2(odom_data):
	print "dados do robot 2"
	global mya
	mya.id = 2
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y

	rtia.updateAttributeValues(mya.myObject,
                     {mya.idHandle:"2 ",
                        mya.batteryHandle:"Bateria ",
                        mya.temperatureHandle: "temperatura ",
                        mya.sensor1Handle:"sensor1 ",
                        mya.sensor2Handle:"sensor2 ",
                        mya.sensor3Handle:"sensor3 ",
                        mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
                        mya.compassHandle:"compass ",
                        mya.gotoHandle:"goto " ,
                        mya.rotateHandle:"rotate ",
                        mya.activateHandle:"activate "},
                        "update")

	
def getPos3(odom_data):
	print "dados do robot 3"
	global mya
	mya.id = 3
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y
	rtia.updateAttributeValues(mya.myObject,
                     {mya.idHandle:"3 ",
                        mya.batteryHandle:"Bateria ",
                        mya.temperatureHandle: "temperatura ",
                        mya.sensor1Handle:"sensor1 ",
                        mya.sensor2Handle:"sensor2 ",
                        mya.sensor3Handle:"sensor3 ",
                        mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
                        mya.compassHandle:"compass ",
                        mya.gotoHandle:"goto " ,
                        mya.rotateHandle:"rotate ",
                        mya.activateHandle:"activate "},
                        "update")

def getPos4(odom_data):
	print "dados do robot 1"
	global mya
	mya.id = 4
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y
	#print pose.position.x
	#print pose.position.y

	rtia.updateAttributeValues(mya.myObject,
		{mya.idHandle:"4 ",
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
        #rtia.tick() #1.0, 1.0)




	
	#rospy.loginfo("Positions %s", data.data)

def getPos5(odom_data):
	print "dados do robot 2"
	global mya
	mya.id = 5
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y

	rtia.updateAttributeValues(mya.myObject,
                     {mya.idHandle:"5 ",
                        mya.batteryHandle:"Bateria ",
                        mya.temperatureHandle: "temperatura ",
                        mya.sensor1Handle:"sensor1 ",
                        mya.sensor2Handle:"sensor2 ",
                        mya.sensor3Handle:"sensor3 ",
                        mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
                        mya.compassHandle:"compass ",
                        mya.gotoHandle:"goto " ,
                        mya.rotateHandle:"rotate ",
                        mya.activateHandle:"activate "},
                        "update")
        #rtia.tick() #1.0, 1.0)

	
def getPos6(odom_data):
	print "dados do robot 3"
	global mya
	mya.id = 6
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y
	rtia.updateAttributeValues(mya.myObject,
                     {mya.idHandle:"6 ",
                        mya.batteryHandle:"Bateria ",
                        mya.temperatureHandle: "temperatura ",
                        mya.sensor1Handle:"sensor1 ",
                        mya.sensor2Handle:"sensor2 ",
                        mya.sensor3Handle:"sensor3 ",
                        mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
                        mya.compassHandle:"compass ",
                        mya.gotoHandle:"goto " ,
                        mya.rotateHandle:"rotate ",
                        mya.activateHandle:"activate "},
                        "update")
        
def getPos7(odom_data):
	print "dados do robot 3"
	global mya
	mya.id = 7
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y
	rtia.updateAttributeValues(mya.myObject,
                     {mya.idHandle:"7 ",
                        mya.batteryHandle:"Bateria ",
                        mya.temperatureHandle: "temperatura ",
                        mya.sensor1Handle:"sensor1 ",
                        mya.sensor2Handle:"sensor2 ",
                        mya.sensor3Handle:"sensor3 ",
                        mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
                        mya.compassHandle:"compass ",
                        mya.gotoHandle:"goto " ,
                        mya.rotateHandle:"rotate ",
                        mya.activateHandle:"activate "},
                        "update")
        

def getPos8(odom_data):
	print "dados do robot 3"
	global mya
	mya.id = 8
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y
	rtia.updateAttributeValues(mya.myObject,
                     {mya.idHandle:"8 ",
                        mya.batteryHandle:"Bateria ",
                        mya.temperatureHandle: "temperatura ",
                        mya.sensor1Handle:"sensor1 ",
                        mya.sensor2Handle:"sensor2 ",
                        mya.sensor3Handle:"sensor3 ",
                        mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
                        mya.compassHandle:"compass ",
                        mya.gotoHandle:"goto " ,
                        mya.rotateHandle:"rotate ",
                        mya.activateHandle:"activate "},
                        "update")
        

def getPos9(odom_data):
	print "dados do robot 3"
	global mya
	mya.id = 9
	pose = odom_data.pose.pose
	mya.posx = pose.position.x
	mya.posy = pose.position.y
	rtia.updateAttributeValues(mya.myObject,
                     {mya.idHandle:"9 ",
                        mya.batteryHandle:"Bateria ",
                        mya.temperatureHandle: "temperatura ",
                        mya.sensor1Handle:"sensor1 ",
                        mya.sensor2Handle:"sensor2 ",
                        mya.sensor3Handle:"sensor3 ",
                        mya.gpsHandle: "<" + str(pose.position.x) + ";" + str (pose.position.y) + "> ",
                        mya.compassHandle:"compass ",
                        mya.gotoHandle:"goto " ,
                        mya.rotateHandle:"rotate ",
                        mya.activateHandle:"activate "},
                        "update")
        
def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")





#### FEDERATION SETUP ##########

print("Create ambassador")
rtia = hla.rti.RTIAmbassador()
mya = MyAmbassador()

#Criando Federacao 
try:
    rtia.createFederationExecution("ExampleFederation", "PyhlaToPtolemy.fed")
    log("Federation created.\n")
except hla.rti.FederationExecutionAlreadyExists:
    log("Federation already exists.\n")

####### Join into a Federation ###############
mya = MyAmbassador()
rtia.joinFederationExecution("uav-recv", "ExampleFederation", mya)
mya.initialize()
log("inicialized!\n")

######### Announce Synchronization Point ######
"""   ---- 
label = "ReadyToRun"
tag =  bytes ("hi!")
rtia.registerFederationSynchronizationPoint(label, tag)
log("Synchronization Point Register!")
while  (mya.isRegistered == False or mya.isAnnounced == False):
	rtia.tick()
print "tick"
--- """
####### Esperando outros Federados ############
x = input ("Waiting for USERS, start aor federations then write a number and press ok.\n")

#######Archieve Synchronized Point  ###########
while (mya.isAnnounced == False):
        rtia.tick()
rtia.synchronizationPointAchieved("ReadyToRun")


#tia.synchronizationPointAchieved("ReadyToRun")

while (mya.isReady == False):
	rtia.tick()
log ("MyAmbassador : Is Ready to run ")

##### Enable Time Policy #####################
currentTime =rtia.queryFederateTime()
lookAhead =1# rtia.queryLookahead()
rtia.enableTimeRegulation(currentTime, lookAhead)
while (mya.isRegulating == False):
	rtia.tick()
rtia.enableTimeConstrained()
while (mya.isConstrained == False):
	rtia.tick()
log("MyAmbassador: Time is Regulating and is Constrained")

###########  CONFIGURACAO E SETUP DO ROS  ###########
log ("\t\t------ STARTING ROS SERVICES -------")

# first thing, init a node!
rospy.init_node('certiListener')

#subscribing a position
rospy.Subscriber("robot_0/odom",  Odometry, getPos)
rospy.Subscriber("robot_1/odom",  Odometry, getPos2)
rospy.Subscriber("robot_2/odom",  Odometry, getPos3)
rospy.Subscriber("robot_3/odom",  Odometry, getPos4)
rospy.Subscriber("robot_4/odom",  Odometry, getPos5)
rospy.Subscriber("robot_5/odom",  Odometry, getPos6)
rospy.Subscriber("robot_6/odom",  Odometry, getPos7)
rospy.Subscriber("robot_7/odom",  Odometry, getPos8)
rospy.Subscriber("robot_8/odom",  Odometry, getPos9)
r = rospy.Rate(2) # hz



while not rospy.is_shutdown():
	###### HLA - Sending data to Federation ######
	print (mya.getPosx())
	print (mya.getPosy())
#	rtia.updateAttributeValues(mya.myObject,
#                        {mya.idHandle:str(mya.getId()),
#                        mya.batteryHandle:"Bateria",
#                        mya.temperatureHandle: "temperatura",
#                        mya.sensor1Handle:"sensor1",
#                        mya.sensor2Handle:"sensor2",
#                        mya.sensor3Handle:"sensor3",
#                        mya.gpsHandle: "<" + str(mya.getPosx()) + ";" + str (mya.getPosy()) + ">",
#                        mya.compassHandle:"compass",
#                        mya.gotoHandle:"goto",
#                        mya.rotateHandle:"rotate",
#                        mya.activateHandle:"activate"},
#                        "update")
#        rtia.tick() #1.0, 1.0)
################## ROS ####################
#Maybe this is necessary to work
	#r.sleep()
	################ HLA #####################
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
