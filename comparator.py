# -*- coding: utf-8 -*-
from Tkinter import *
import rospy
from nav_msgs.msg import Odometry





class Application(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.msg = Label(self, text="Foi detectada uma diferença superior ao esperado entre o caminho dos robõs")
		self.msg.pack ()
		self.bye = Button (self, text="Fechar Janela", command=self.quit)
		self.bye.pack ()
		self.pack()



global posicaoRobo1
global posicaoRobo2

posicaoRobo1 = None
posicaoRobo2 = None

def getPos1(odom):
	global posicaoRobo1
	posicaoRobo1 = odom

def getPos2(odom):
	global posicaoRobo2
	posicaoRobo2 = odom

def compare():
	global posicaoRobo1
	global posicaoRobo2
	if (posicaoRobo1 == None) or (posicaoRobo2 == None):
		return False
	xa, ya = posicaoRobo1.pose.pose.position.x, posicaoRobo1.pose.pose.position.y
	xb, yb = posicaoRobo2.pose.pose.position.x, posicaoRobo2.pose.pose.position.y
	distancia = math.hypot(xa - xb, ya - yb)
	if (distancia > 7):
		return True
	return False


#Serviços do ros
import sys
import rospy
import math
#Start the node
rospy.init_node ( "comparator_manager")

#ROS configurations 
robot1 , robot2 = sys.argv[1], sys.argv[2]

rospy.Subscriber("/robot_"+ robot1 + "/base_pose_ground_truth", Odometry, getPos1)
rospy.Subscriber("/robot_"+ robot2 +"/base_pose_ground_truth", Odometry, getPos2)
r = rospy.Rate(10)


while not rospy.is_shutdown():
	#compara distancia de robôs
	if (compare()):
		app = Application()
		app.master.title("Simulator Manager")
		mainloop()
		break
	r.sleep()
