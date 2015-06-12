import ptolemy.data
import math

global ultimaVelocidade
ultimaVelocidade = 0


class Main :
	def __init__ (self):
		self.lex= 0
		self.ley= 0
		self.lez= 0
		self.mId= 0
		self.mmx=0
		self.mmy=0
		self.mmz=0
		self.pontos= [ [10,10],  [10,-10], [-10,-10], [-10,10] ]
		self.contadorPosicao = 0
	
	def whereImGoing(self):
		lx= float (self.lex)
		ly= float (self.ley)
		lz= float (self.lez)
		myId= str (self.mId)
		if (myId == "0"): # Im the leader
			return pontos[contadorPosicao][0], pontos[contadorPosicao][1]
		elif (myId == "1"):
			return lx -1 , ly-1
		elif (myId == "2"):
			return lx + 1 , ly-1
		return 0, 0


	def calculaVelocidadeLinear(self, distanciaAlvo):
		global ultimaVelocidade
		lastVel = ultimaVelocidade
		MAX_VELOCIDADE_LINEAR = 1
		ACELERACAO_LINEAR = 0.05
		velocidadeLinear = 0
		#Acelerando
		if (distanciaAlvo >= 4):
			velocidadeLinear = lastVel + ACELERACAO_LINEAR
			if velocidadeLinear> MAX_VELOCIDADE_LINEAR:
				velocidadeLinear = MAX_VELOCIDADE_LINEAR
			return float (velocidadeLinear)
		#desacelerando
		else:
			velocidadeLinear = velocidadeLinear - ACELERACAO_LINEAR
			if velocidadeLinear< ACELERACAO_LINEAR:
				velocidadeLinear = ACELERACAO_LINEAR
			return float (velocidadeLinear)



	def myPosition(self):
		return self.mmx, self.mmy, self.mmz

	def walkon(self):
		return 1, 0 #linear and angular
	def walkhorario(self):
		return 0, -0.5 #linear and angular
	def walkantihorario(self):
		return 0, 0.5 #linear and angular
	def walkback(self):
		return -1, 0 #linear and angular

	def degrees(self, value):
		return ((value* 180.0)/math.pi)

#Walking and redirecting
	def walkhorarioon(self, vel):
		return float (vel), -0.5 #linear and angular
	def walkantihorarioon(self, vel):
		return float (vel), 0.5 #linear and angular
	def walkonhorario(self):
		return 1, -0.1 #linear and angular
	def walkonantihorario(self):
		return 1, 0.1 #linear and angular



	def isOriented(self):
		x, y = self.whereImGoing()
		mx, my, mz = self.myPosition()
		if (not (mx == 0 and my == 0)):
			#calcula a distancia entre meu ponto e o ponto que quero ir
			hip = math.hypot (x - mx, y - my)
			#calcula a distancia dos dois catetos
			tmp1 = math.hypot( x -mx, 0 )
			tmp2 = math.hypot( 0, y -my )
			#seleciona o maior cateto
			cat = max ([tmp1, tmp2])
			#calcula o angulo que preciso estar para
			anguloEsperado = self.degrees(math.cos(float(cat)/hip))
			deltax = x - mx
			deltay = y - my
			deltax = abs(deltax)
			deltay = abs(deltay)
			if (deltax<0.19) and y > my:
			        anguloEsperado = 90
			elif (deltax<0.19) and y < my:
			        anguloEsperado = 270
			elif (deltay<0.19) and mx < x:
			        anguloEsperado = 0
			elif (deltay<0.19) and mx > x:
			        anguloEsperado = 180
			elif mx < x and my <=y:
			        pass#anguloEsperado += 180 
			elif mx < x and my >= y:
			        anguloEsperado= anguloEsperado +270# = 180 - anguloEsperado
			elif mx > x and my <= y:
			        anguloEsperado= anguloEsperado + 90# = 360 - anguloEsperado
			elif mx > x and my >= y:
			        anguloEsperado =anguloEsperado + 180# anguloEsperado
			a = max ([anguloEsperado, mz])
			b = min ([anguloEsperado , mz])
			self.log.broadcast(ptolemy.data.StringToken("AE: "+ str(anguloEsperado) + " MA: "+ str(mz)))
			limin = 3
			if ((a - b) < limin or ((a-b)>(360-limin))):
			        return True , anguloEsperado, mz, hip
			return False, anguloEsperado, mz, hip
		return False, 1000, 800, 1000


	def inPosition(self):
		x, y = self.whereImGoing()
		mx, my, mz = self.myPosition()
		if ((math.hypot(x-mx, y-my))< 0.3):
			self.contadorPosicao = (self.contadorPosicao + 1)%len(self.pontos)
			global ultimaVelocidade
			ultimaVelocidade = 0
		        return True
		return False


	def walk (self):
		x, y = self.whereImGoing()
		self.log.broadcast(ptolemy.data.StringToken("Im Going to -  X: "+ str(x) + " Y: "+ str(y)))
		mx, my, mz = self.myPosition()
		myId= str (self.mId)
	        if (not self.inPosition()):
	                orient, ang, mz, hip = self.isOriented()
	                if (orient):
				#muito Orientado
				if (int (mz) == int (ang) ):
					self.log.broadcast(ptolemy.data.StringToken("em frente "))
	                        	return self.walkon()
				#Orientado mas necessita de ajustes TODO: NO ORIGINAL TEM UM ELIF
				else:
					if ((ang-mz) >= 0):
						if (ang-mz)< 180:
							return self.walkonantihorario()
						else:
							return self.walkonhorario()
					else:
						if (abs(ang-mz) < 180):
							return self.walkonhorario()
						else:
							return self.walkonantihorario()
			#Não está orientado, com distancia curta TODO provavelmente elif ou if nao faz diferenca nesse caso por causa do return
			if hip < 2.3:
			        if ((ang - mz) >= 0):
					if ((ang- mz) < 180):
						return self.walkantihorario()
					else: 
						return self.walkhorario()
				elif((ang- mz) < 0):
					if (abs((ang- mz)) < 180):
						return self.walkhorario()
					else: 
						return self.walkantihorario()
			#Não está orientado, possuindo grande distancia ao alvo
			else:
				velocidade = self.calculaVelocidadeLinear(hip)
			        if ((ang - mz) >= 0):
					if ((ang- mz) < 180):
						return self.walkantihorarioon(velocidade)
					else: 
						return self.walkhorarioon(velocidade)
				elif((ang- mz) < 0):
					if (abs((ang- mz)) < 180):
						return self.walkhorarioon(velocidade)
					else: 
						return self.walkantihorarioon(velocidade)
		return 0, 0


	def whereImGoing(self):
		lx= float(self.lex)
		ly= float (self.ley)
		lz= float(self.lez)
		myId = self.mId
		distance = 2
		if (myId == "0"): # Im the leader
#			return self.pontos[self.contadorPosicao][0], self.pontos[self.contadorPosicao][1]
			return 10,10
		elif (myId == "1"):
			return lx -distance , ly - distance
		elif (myId == "2"):
			return lx + distance , ly  - distance
		return 0, 0

	def graus(self, value):
		return (value*180.0) /math.pi

	def fire(self) :
		#self.output.broadcast("fala negada")
		self.mId = str(self.myId.get(0).stringValue())
		#leader position
		self.lex  = self.lx.get(0).stringValue()
		self.ley  = self.ly.get(0).stringValue()
		self.lez = self.lz.get(0).stringValue()
		#my position
		self.mmx  = self.mx.get(0).doubleValue()
		self.mmy  = self.my.get(0).doubleValue()
		self.mmz  = self.mz.get(0).doubleValue()
		linear, angular = self.walk()
		global ultimaVelocidade
		ultimaVelocidade = float(linear)
		self.linear.broadcast(ptolemy.data.DoubleToken(linear))
		self.angular.broadcast(ptolemy.data.DoubleToken(angular))
		return
