# -*- coding: utf-8 -*-
import rospy
from geometry_msgs.msg import Twist

from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Imu
import socket
import tf

global SERVERPORT
SERVERPORT =  "6000"   #the port users will be connecting to

global V
global W
global myNumber
global x
global y 
global teta
global q1 
global q2
global q3
global q4

global used_imu
used_imu = True

def send_data(mynumber, port):
	global V
	global W
	global x
	global y
	global q3
	global q4
	message = str(mynumber)+" "+ str(0.0)+" "+str(0.0)+" "+str(x)+" "+str(y)+" "+str(q3)+" "+str(q4)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(message, ("127.0.0.1", int (port)))
	sock.close()

#Lê do ROS os valores do IMU: roll, pitch e yaw
#Subscribe no Topico /mobile_base/sensors/imu_data
def imu_data (data):
	global imu
	imu = data;
	global used_imu
	used_imu = false;
	#TODO entender essa parte aqui 
	#double yaw,pitch,roll;
	#tf::Quaternion q;
	euler = tf.transformations.euler_from_quaternion(data.orientation)
	#tf::quaternionMsgToTF(data.orientation, q);
	roll = euler[0]
	pith = euler[1]
	yaw  = euler[2]
	#tf::Matrix3x3(q).getEulerYPR(yaw, pitch, roll);
	#//ROS_INFO("I Receive Imu:\n yaw:%f\n pitch:%f\n roll:%f ", yaw,pitch,roll);

#//Lê do ROS os valores da velocidade linear e angular: V e W 
#//Subscribe no Topico cmd_vel_mux/input/teleop
def  cmd_vel_callback(vel_cmd):
	global V
	V = vel_cmd.linear.x;
	global W
	W = vel_cmd.angular.z;


#Lê do ROS os valores de posição: x, y e teta
#Subscribe no Topico odom + Send Data
def odomCallback(odom, numberRobot, porta):
	global x
	global y
	global q1
	global q2
	global q3
	global q4
	x = odom.pose.pose.position.x
	y = odom.pose.pose.position.y
	q1 = odom.pose.pose.orientation.x
	q2 = odom.pose.pose.orientation.y
	q3 = odom.pose.pose.orientation.z
	q4 = odom.pose.pose.orientation.w
	send_data(numberRobot,porta);
    
def odomCallback1(odom):
	odomCallback(odom, 1, "6000")
def odomCallback2(odom):
	odomCallback(odom, 2, "6002")
def odomCallback3(odom):
	odomCallback(odom, 3, "6003")


global V

import rospy

rospy.init_node('PublisherTurtle')

rospy.Subscriber("/commands/velocity", LaserScan, cmd_vel_callback)
rospy.Subscriber("/odom", Odometry, odomCallback1)
rospy.Subscriber("/sensors/imu_data", Imu, imu_data)

rospy.Subscriber("/robot1/commands/velocity", LaserScan, cmd_vel_callback)
rospy.Subscriber("/robot1/odom", Odometry, odomCallback1)
rospy.Subscriber("/robot1/sensors/imu_data", Imu, imu_data)

rospy.Subscriber("/robot2/commands/velocity", LaserScan, cmd_vel_callback)
rospy.Subscriber("/robot2/odom", Odometry, odomCallback2)
rospy.Subscriber("/robot2/sensors/imu_data", Imu, imu_data)

rospy.Subscriber("/robot3/commands/velocity", LaserScan, cmd_vel_callback)
rospy.Subscriber("/robot3/odom", Odometry, odomCallback3)
rospy.Subscriber("/robot3/sensors/imu_data", Imu, imu_data)
p = rospy.Publisher("/mobile_base/commands/velocity", Twist)
p1 = rospy.Publisher("/robot1/commands/velocity", Twist)
p2 = rospy.Publisher("/robot2/commands/velocity", Twist)
p3 = rospy.Publisher("/robot3/commands/velocity", Twist)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 6001))

while not rospy.is_shutdown():
	data, addr = sock.recvfrom(1024) 
	robotId, V, W = data.split(" ")
	twist = Twist()
	twist.linear.x = float (V)
	twist.angular.z = float (W) 
	p.publish(twist)

