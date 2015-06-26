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
import hla.rti
import hla.omt as fom
import struct


################################
#   The  Ambassador class      #
################################

import time
getTime = lambda: int(round(time.time() * 1000))

class MyAmbassador(hla.rti.FederateAmbassador):
	def initialize(self, value, number=""):
		self._rtia = value
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

		self.listaDados = []

		#Handles to manipulate data from CERTI - RTIG

		self.classHandle = self._rtia.getObjectClassHandle("ObjectRoot.robot"+str(number))
		self.log ("Using object ObjectRoot.robot"+str(number))
		self.idHandle = self._rtia.getAttributeHandle("id", self.classHandle)
		self.batteryHandle = self._rtia.getAttributeHandle("battery", self.classHandle)
		self.temperatureHandle = self._rtia.getAttributeHandle("temperature", self.classHandle)
		self.sensor1Handle = self._rtia.getAttributeHandle("sensor1", self.classHandle)
		self.sensor2Handle = self._rtia.getAttributeHandle("sensor2", self.classHandle)
		self.sensor3Handle = self._rtia.getAttributeHandle("sensor3", self.classHandle)
		self.gpsHandle = self._rtia.getAttributeHandle("gps", self.classHandle)
		self.compassHandle = self._rtia.getAttributeHandle("compass", self.classHandle)
		self.gotoHandle = self._rtia.getAttributeHandle("goto", self.classHandle)
		self.rotateHandle = self._rtia.getAttributeHandle("rotate", self.classHandle)
		self.activateHandle = self._rtia.getAttributeHandle("activate", self.classHandle)
		#Subscribe HLA
		self._rtia.subscribeObjectClassAttributes(self.classHandle,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		#Publish HLA
		self._rtia.publishObjectClass(self.classHandle,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
		self.myObject = self._rtia.registerObjectInstance(self.classHandle)#, "ROBO_2")
	###########################
	#Calbacks from CERTI - HLA#
	###########################
	def reflectAttributeValues(self, object, attributes, tag, order, transport, time=None, retraction=None):
		attMap = {}
		attMap["time"] = getTime()
		attMap["id"] = attributes[self.idHandle]
		attMap["battery"]= attributes[self.batteryHandle]
		attMap["temperature"]= attributes[self.temperatureHandle]
		attMap["sensor1"]= attributes[self.sensor1Handle]
		attMap["sensor2"]= attributes[self.sensor2Handle].replace("sensor2:","").replace("\x00","")
		attMap["sensor3"]= attributes[self.sensor3Handle]
		attMap["gps"] = attributes[self.gpsHandle]
		attMap["compass"] = attributes[self.compassHandle]
		attMap["goto"] = attributes[self.gotoHandle]
		attMap["rotate"]= attributes[self.rotateHandle]
		attMap["activate"]= attributes[self.activateHandle]
		self.listaDados.append(attMap)

	def hasData (self):
		return (len (self.listaDados)>0)
	def getData (self):
		return self.listaDados.pop(0)

	def log (self, valor):
		print ("\033[34m" + valor + "\033[0;0m")

	def terminate(self):
		self._rtia.deleteObjectInstance(self.myObject, "ROBO_2")

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
		self._rtia.requestObjectAttributeValueUpdate(object,[self.idHandle, self.batteryHandle, self.temperatureHandle, self.sensor1Handle, self.sensor2Handle, self.sensor3Handle, self.gpsHandle, self.compassHandle, self.gotoHandle, self.rotateHandle, self.activateHandle])
	def timeAdvanceGrant (self, time):
		self.advanceTime = True

