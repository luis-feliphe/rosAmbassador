# -*- coding: utf-8 -*-

#####################################################
# This code is responsible by listen events on ROS  #
# and publish on CERTI - HLA.                       #
#####################################################

import time
import sys
import string
import math
from threading import Thread
#CERTI
from MyAmbassador import MyAmbassador
import hla.rti
#ROS 
import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
import threading

####### Unused ###########
#from sensor_msgs.msg import LaserScan
#from geometry_msgs.msg import Quaternion
#import random
#import hla.omt as fom
#import struct
#from parser import Parser
##########################


##########################
## Variaveis globais  ####
##########################
##########################
global SIMULATE_ERROR
SIMULATE_ERROR =True 

##### Log robô Simulado ###
global entrada
global saida
global contadorentrada
global contadorsaida
contadorentrada = 0
entrada = {}
saida={}
contadorsaida = 0

#### Log do Robôo real ####
global saidaReal
global contadorSaidaReal
saidaReal = {}
contadorSaidaReal = 0
##########################


global mya
global on 
on = True
global cont
cont = 0
global dataToSend
dataToSend=None
#########################
global listaPosicoes
listaPosicoes= []
global positions
positions = {}

global mapaInicio
mapaInicio={}
global mapaFim
mapaFim= {}
global newConter
newConter = 0

global teste
teste = []

##########################

global listaPosicoes
listaPosicoes = []
global VEL_MAX #maxima velocidade possivel 
VEL_MAX = 0.6
global dataToSend
dataToSend=None
global posicoes
posicoes= {}
global contpos
contpos = 0
global ultimavelocidade
ultimavelocidade = 0
global IteracoesROS
IteracoesROS = 1


global k 
k = []
#
#
#
#
#




###########################
## Algoritmo de controlo ##
###########################
######  Funcoes  ##########
###########################




def log (valor):
        print ("\033[36m" + valor + "\033[0;0m")

#TODO TA ERRADO AQUI 
def whereImGoing():
	#TODO: SEMPRE SOU O ROBO 1 (REAL)
	global positions
	if positions.has_key("leader"):
		return positions["leader"][0]-2, positions["leader"][1]-2
	return 0, 0

def calculaVelocidadeLinear(distanciaAlvo):
        global ultimavelocidade
        lastVel = ultimavelocidade
        #Velocidade linear maxima a ser enviada pelo robo 
        MAX_VELOCIDADE_LINEAR= 0.5
        ACELERACAO_LINEAR = 0.05
        velocidadeLinear = 0
        #acelerando ou continua
        if (distanciaAlvo>=4):
                velocidadeLinear = lastVel+ ACELERACAO_LINEAR
                if velocidadeLinear > MAX_VELOCIDADE_LINEAR:
                        velocidadeLinear= MAX_VELOCIDADE_LINEAR
                return float(velocidadeLinear)
        #desacelerando
        else:
                velocidadeLinear = velocidadeLinear - ACELERACAO_LINEAR
                if velocidadeLinear < ACELERACAO_LINEAR:
                        velocidadeLinear = ACELERACAO_LINEAR
                return float(velocidadeLinear)

def stop():
        return Twist()
        t.linear.x = 0.3
def walkon():
        global VEL_MAX
        t = Twist()
        t.linear.x = VEL_MAX #modificado1
        return t

def walkhorario():
        global VEL_MAX
        t = Twist()
        t.angular.z =-VEL_MAX #modificado -0.5
        #t.linear.x = 0.2
        return t

def walkantihorario():
        global VEL_MAX
        t = Twist()
        t.angular.z = VEL_MAX #modificado 0.5
        #t.linear.x = 0.2
        return t


def walkhorarioon(vel):
        global VEL_MAX
        t = Twist()
        t.angular.z = -VEL_MAX #modificado -0.5
#t.linear.x = 0.3# 0.3
        t.linear.x = 0.3#vel# 0.3
        return t

def walkantihorarioon(vel):
        global VEL_MAX
        t = Twist()
        t.angular.z =VEL_MAX # modificado 0.5
        t.linear.x = 0.3
#       t.linear.x = vel# 0.3
        return t
def walkonhorario():
        global VEL_MAX
        t = Twist()
        t.angular.z = -0.3# modificando 1
        t.linear.x = VEL_MAX #1 - modificado
        return t

def walkonantihorario():
        global VEL_MAX
        t = Twist()
        t.angular.z = 0.3 #modificando 1
        t.linear.x = VEL_MAX #modificado 1
        return t

def myPosition():
        global positions
	if positions.has_key ("real"):
		return positions["real"] #= [round (odom.pose.pose.position.x), round (odom.pose.pose.position.y), round (getDegreesFromOdom(odom))]
        return 0,0, 0


def isOriented(x, y, mx, my, mz):
        if (not (mx == 0 and my == 0)):
                #calcula a distancia entre meu ponto e o ponto que quero ir
                hip = math.hypot (x - mx, y - my)
                #calcula a distancia dos dois catetos
                tmp1 = math.hypot( x -mx, 0 )
                tmp2 = math.hypot( 0, y -my )
                #seleciona o maior cateto
                cat = max ([tmp1, tmp2])
                #calcula o angulo que preciso estar para
                anguloEsperado = degrees(math.cos(float(cat)/hip))
                deltax = x - mx
                deltay = y - my
                deltax = abs(deltax)
                deltay = abs(deltay)
               #print anguloEsperado
                if (deltax<0.19) and y > my:
                        anguloEsperado = 90
                elif (deltax<0.19) and y < my:
                        anguloEsperado = 270
                elif (deltay<0.19) and mx < x:
                        anguloEsperado = 0
                elif (deltay<0.19) and mx > x:
                        #print "era pra andar pra esquerda"
                        anguloEsperado = 180
                elif mx < x and my <=y:
                        pass#anguloEsperado += 180 
                elif mx < x and my >= y:
                        anguloEsperado= anguloEsperado +270# = 180 - anguloEsperado
                elif mx > x and my <= y:
                        anguloEsperado= anguloEsperado + 90# = 360 - anguloEsperado
                elif mx > x and my >= y:
                        anguloEsperado =anguloEsperado + 180# anguloEsperado
                #mz =  mz + 180
                a = max ([anguloEsperado, mz])
                b = min ([anguloEsperado , mz])
                #print "values " + str (anguloEsperado) + " - " + str (mz) + " = " + str (a - b)
                limin =3
                if ((a - b) < limin or ((a-b)>(360-limin))):
                        return True , anguloEsperado, mz, hip
                return False, anguloEsperado, mz, hip
        return False, 1000, 800, 1000


def inPosition(x, y, mx, my, mz):
#        x, y = whereImGoing()
#       mx, my, mz = myPosition()
        if ((math.hypot(x-mx, y-my))< 0.3):
                global contpos
                contpos = (contpos + 1)%4
                global ultimavelocidade
                ultimavelocidade = 0
                return True
	return False


def walk (x, y, mx, my, mz):
	global myId
	if (not inPosition(x, y, mx, my, mz)):
		orient, ang, mz, hip = isOriented(x, y, mx, my, mz)
		#Minimamente orientado
		if (orient):
			#Muito orientado 
			if (int (ang) == int(mz)):
				return walkon()
			#orientado mas necessita de poucos ajustes
			else:
				if ((ang - mz) >= 0 ):
					if ((ang-mz)<180):
						return walkonantihorario()
					else:
						return walkonhorario()
				else:#if ((ang-mz)<0):
					if (ang-mz)<180:
						return walkonhorario()
					else:
						return walkonantihorario()
		#nao esta orientado com distancia curta
		if (hip < 1.5):
			if ((ang - mz) >= 0 ):
				if ((ang-mz)<180):
					return walkantihorario()
				else:
					return walkhorario()
			elif ((ang-mz)<0):
				if (abs(ang-mz)<180):
					return walkhorario()
				else:
					return walkantihorario()
	       #Nao esta orientado com distancia maior
		else:
			velocidade = 0.5#calculaVelocidadeLinear(hip)
			if ((ang - mz) >= 0 ):
				if ((ang-mz)<180):
					return walkantihorarioon(velocidade)
				else:
					return walkhorarioon(velocidade)
			elif ((ang-mz)<0):
				if (abs(ang-mz)<180):
					return walkhorarioon(velocidade)
				else:
					return walkantihorarioon(velocidade)

	return stop()
#	return None
def getxy (odom):
        return round (odom.pose.pose.position.x), round ( odom.pose.pose.position.y), round (getDegreesFromOdom (odom))#degrees(yall)

def degrees(value):
	return ((value * 180.0)/math.pi)

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
#def sendData(lista):
#	idrobot = lista[0]
#	battery=lista [1]
#	temperature=lista [2]
#	sensor1=lista[3]
#	sensor2=lista[4]
#	sensor3=lista[5]
#	gps=lista[6]
#	compass=lista[7]
#	goto=lista[8]
#	rotate=lista[9]
#	activate=lista[10]
#print (str (sensor1) + " "  + str(sensor2)  + " " + str(gps.split(";")[0])  + " " + str(gps.split(";")[1])+ " " + str(gps.split(";")[1]))
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

def sendData2(idrobot ,battery="", temperature="", sensor1="", sensor2="", sensor3="", gps="<0;0>",compass="", goto="", rotate="", activate=""):
	global k
	k.append([idrobot, battery, temperature, sensor1, sensor2, sensor3, gps, compass, goto, rotate, activate])


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
if (mId == "22"):
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


############################
##### Calbacks do ROS  #####
############################
def getPos0(odom):
	global positions
	positions["leader"] = [round (odom.pose.pose.position.x), round (odom.pose.pose.position.y), round (odom.pose.pose.orientation.w)]
def getPos1(odom):
	global positions
	positions["my"] = [round (odom.pose.pose.position.x), round (odom.pose.pose.position.y), round (getDegreesFromOdom(odom))]

def getPosReal(odom):
	global positions
	positions["real"] = [round (odom.pose.pose.position.x), round (odom.pose.pose.position.y), round (getDegreesFromOdom(odom))]
def hasDataGeneral():
	global positions
	return positions.has_key("leader") and positions.has_key("real")
	#return positions.has_key("my") and positions.has_key("leader") and positions.has_key("real")



#############################
# Administracao dos Topicos #
#############################
rospy.Subscriber("/robot_0/base_pose_ground_truth",  Odometry, getPos0)
rospy.Subscriber("/robot_" + str (mId[0]) +  "/base_pose_ground_truth",  Odometry, getPos1)
rospy.Subscriber("/robot_1/base_pose_ground_truth",  Odometry, getPosReal)

#global p
#p = rospy.Publisher("robot_" + str(mId[0])+ "/cmd_vel", Twist)
global p2
p2 = rospy.Publisher("robot_" + str(mId[0])+ "/cmd_vel", Twist)
#global r


cont = 0
on = True
global contadorRos2
contadorRos2 = 0
################
## Main loop  ##
################
iteracoes = 0.0

def rosLoop (oi):
	r = rospy.Rate(300) # hz
	real = rospy.Publisher("robot_1/cmd_vel", Twist)
	while not rospy.is_shutdown():
		global IteracoesROS

		###################################
		### Bridge Sending Data to HLA  ###
		##################################
		if hasDataGeneral():
#			print "----------------------------------------------"
			#lock = threading.Lock()
			#lock.acquire()
			global contadorRos2
			contadorRos2+=1
			x, y = whereImGoing()
			mx, my, mz = myPosition()
			global newConter
			newConter+= 1
			global positions
			global mapaInicio
			mapaInicio[str(newConter)]=getTime()
			#Adicionando ao log: leaderX, leaderY, leaderZ, posX, posY, posZ 
			global entrada
			global contadorentrada
			global mId
#			print "1a : "+str(positions["leader"][0])+ " " + str( (positions["leader"][1]))+ " " + str (mx)+ " " + str (my)+ "*" + str(mz)
			entrada[contadorentrada]=str(positions["leader"][0])+ " " + str( (positions["leader"][1]))+ " " + str (mx)+ " " + str (my)+ "*" + str(mz)
#			print "2a : " + str (entrada[contadorentrada])
			contadorentrada+= 1
			#TODO PRESTAR ATENCAO AQUI .... 
			sendData(int (mId), "", "", positions["leader"][0], positions["leader"][1], positions["leader"][2], "<" + str(mx)+   ";"  + str(my) + ";" + str(mz)+ ">", "", "", "", str ( newConter ))
			valor = walk(x, y, mx, my, mz)
			ultimaVelocidade = valor.linear.x
#			if (SIMULATE_ERROR and IteracoesROS > 200):
#				valor = Twist()
#				valor.angular.z =1
#				valor.linear.x = 1
			real.publish(valor)
			global contadorSaidaReal
			global saidaReal
			saidaReal[contadorSaidaReal] =  str (valor.linear.x) + " | " + str (valor.angular.z)
			contadorSaidaReal += 1
			#lock.release()
			### Limpando Variaveis ###
		if (SIMULATE_ERROR and IteracoesROS > 100):
			print "CHEGOU AQUI " 
			valor = Twist()
			valor.angular.z =0.5
			valor.linear.x = 1
			real.publish(valor)
		#positions= {}
		IteracoesROS += 1
		r.sleep()

tempoInicial = getTime()
th= Thread(target= rosLoop, args=("", ))
th.start()

try:
	while not rospy.is_shutdown():
		iteracoes+= 1
		######################################
		######### Sending Data to HLA ########
		######################################		
		global k
#		if (len (k) > 0):
#			sendData(k.pop(0))
		

		######################################
		### Bridge handling data from  HLA  ##
		######################################
		if mya.hasData():
			attMap2 = mya.getData()
			_goto = attMap2["goto"]
			_tempo = attMap2["time"]
			_rid = attMap2["id"]
			_iteracoes = attMap2["activate"]
			_iteracoes= _iteracoes.replace("\\", "").replace("\"", "").replace(";", "").replace(" ", "").replace("\x00", "")

			#print ("o que chegou - " + str (_iteracoes) + " - " + str (_tempo)) 
			if (_rid.count(str (3) ) ==1):
				#Walk
				if (_goto.count("none")<1 and _goto.count(";")== 1):
					global mapaFim
					mapaFim[str(_iteracoes)]=float (_tempo)
					global teste
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
					saida[contadorsaida] = str (round(float(lin),2)) + " | " + str (round(float(ang),2))
					teste.append(str (round(float(lin),2)) + " | " + str (round(float(ang),2)))
					contadorsaida += 1
					twist.linear.x = round (float (lin), 2)
					twist.angular.z = round (float (ang), 2)
					p2.publish (twist)
			#mya.hasData = False
			#mya.attMap = {}
			

		#######  Time Management  ########
		timeHLA = rtia.queryFederateTime() + 1
		rtia.timeAdvanceRequest(timeHLA)
		#print ("Tempo Atual no HLA = " , timeHLA)
		while (mya.advanceTime == False):
			rtia.tick()
		mya.advanceTime = False
		#################################
	#		_time = int(round(time.time()*1000))

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
	print "total Real" + str (total/float(contadorRos2))
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



	#Provavelmente esse eh o grafico do tempo 
	arquivo = open ("./sim/Simulacao_Robo_"+str (mId) + ".txt", "w")
	for i in range (0, len (eixoindice)):
		arquivo.write(str (eixoindice[i]) +":"+str(eixovalor[i])+"\n")
	arquivo.close()

	####Log system#####
	global saida
	global saidaReal

	logFile = open ("./sim/logsimulacaoSimulado"+ str (mId)+".txt", "w")
	for i in entrada.iterkeys():
		if (saida.has_key(i)):
			logFile.write(entrada[i] + " : " + saida[i]+ "\n")
	logFile.close()
		


	logFile = open ("./sim/saida"+ str (mId)+".txt", "w")
	for i in teste:
		logFile.write(str(i)+ "\n")
	logFile.close()
		


	logFile = open ("./sim/logsimulacaoReal"+ str (mId)+".txt", "w")
	for i in entrada.iterkeys():
		if (saidaReal.has_key(i)):
			logFile.write(entrada[i] + " : " + saidaReal[i]+ "\n")
	logFile.close()
	
	
mya.terminate()
rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)
print("Done.")
