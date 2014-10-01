#!/usr/bin/env python

""" Example code of how to move a robot forward for 3 seconds. """

# We always import roslib, and load the manifest to handle dependencies


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
		######## Configurando objetos a serem recebidos ##############

		self.classHandle = rtia.getObjectClassHandle("ObjectRoot.robot")

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

		rtia.subscribeObjectClassAttributes(self.classHandle,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		##############################################################
		rtia.publishObjectClass(self.classHandle,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
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
		self.log("Valores: Bateria: " +str (bateria) + "; Temperatura: " + str(temperatura) + "; GPS: " + str (gps))

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
		rtia.requestObjectAttributeValueUpdate(object,[self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
	def timeAdvanceGrant (self, time):
		self.advanceTime = True



#Metodos

def getPos(odom_data):
	pose = odom_data.pose.pose
	print pose.position.x
	print pose.position.y
	print "\n"
	#rospy.loginfo("Positions %s", data.data)

def log (valor):
	print ("\033[36m" + valor + "\033[0;0m")





####  CONFIGURAcaO E SETUP DA FEDERACAO ##########

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
label = "ReadyToRun"
tag =  bytes ("hi!")
rtia.registerFederationSynchronizationPoint(label, tag)
log("Synchronization Point Register!")
while  (mya.isRegistered == False or mya.isAnnounced == False):
	rtia.tick()
print "tick"

####### Esperando outros Federados ############
x = input ("Waiting others federators\n")

#######Archieve Synchronized Point  ###########
rtia.synchronizationPointAchieved("ReadyToRun")
while (mya.isReady == False):
	rtia.tick()
log ("MyAmbassador : Is Ready to run ")

##### Enable Time Policy #####################
currentTime =rtia.queryFederateTime()
lookAhead = rtia.queryLookahead()
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
rospy.init_node('move')

# publish to cmd_vel
p = rospy.Publisher("/cmd_vel", Twist)
#subscribing a position
rospy.Subscriber("odom",  Odometry, getPos)
r = rospy.Rate(2) # hz


while not rospy.is_shutdown():
	###### HLA - Sending data to Federation ######
	rtia.updateAttributeValues(mya.myObject,
                        {mya.batteryHandle:"ValorBBB",
                        mya.temperatureHandle: "Valor BBB ",
                        mya.sensor1Handle:"ValorBBB",
                        mya.sensor2Handle:"Valor BBB",
                        mya.sensor3Handle:"Valor BBB",
                        mya.gpsHandle: "Valor BBB ",
                        mya.compassHandle:"ValorBBB",
                        mya.gotoHandle:"ValorBBB",
                        mya.rotateHandle:"ValorBBB",
                        mya.activateHandle:"ValorBBB"},
                        "update")

        rtia.tick(1.0, 1.0)
	################## ROS ####################
	# create a twist message, fill in the details
	twist = Twist()
	twist.linear.x = random.randint(1, 100);
	twist.angular.z = random.randint(1, 100);

	# announce move, and publish the message
	rospy.loginfo("Enviando a mensagem ")
	p.publish(twist)
	r.sleep()
	################ HLA #####################
	#######  Time Management  ########
	time = rtia.queryFederateTime()
	rtia.timeAdvanceRequest(time)
	while (mya.advanceTime == False):
		rtia.tick()
	mya.advanceTime = False
	#################################


mya.terminate()
rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)
print("Done.")
