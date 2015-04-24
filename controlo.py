import ptolemy.data
import math



class Main :
	def __init__ (self):
		self.lex= 0
		self.ley= 0
		self.lez= 0
		self.mId= 0
		self.mmx=0
		self.mmy=0
		self.mmz=0
	
	def whereImGoing(self):
		lx= float (self.lex)
		ly= float (self.ley)
		lz= float (self.lez)
		myId= str (self.mId)

		if (myId == "0"): # Im the leader
			return (0, 0)
		elif (myId == "1"):
			return lx -1 , ly-1
		elif (myId == "2"):
			return lx + 1 , ly-1
		return 0, 0


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
			limin = 9
			if ((a - b) < limin or ((a-b)>(360-limin))):
			        return True , anguloEsperado, mz
			return False, anguloEsperado, mz
		return False, 1000, 800


	def inPosition(self):
		x, y = self.whereImGoing()
		mx, my, mz = self.myPosition()
		if ((math.hypot(x-mx, y-my))< 0.3):
		        return True
		return False


	def walk (self):
		x, y = self.whereImGoing()
		mx, my, mz = self.myPosition()
		myId= str (self.mId)
		if (myId == "0"): # Im the leader
			self.log.broadcast(ptolemy.data.StringToken("Em frente"))
			return walkon()
		else:
		        if (not self.inPosition()):
		                orient, ang, mz = self.isOriented()
		                if (orient):
					self.log.broadcast(ptolemy.data.StringToken("em frente "))
		                        return self.walkon()
		                if ((ang - mz) > 0):
					self.log.broadcast(ptolemy.data.StringToken("antihorario"))
					if ((ang- mz) < 180):
						return self.walkantihorario()
					else: 
						return self.walkhorario()
				elif((ang- mz) < 0):
					if (abs((ang- mz)) < 180):
						return self.walkhorario()
					else: 
						return self.walkantihorario()
				else:
					self.log.broadcast(ptolemy.data.StringToken("Deu aguia"))
		        else:
				self.log.broadcast(ptolemy.data.StringToken("em posicao "))
				return 0, 0


#		                if ((ang - mz) > 0):# and (ang-mz) < 180):
#					self.log.broadcast(ptolemy.data.StringToken("antihorario"))
#					return self.walkantihorario()
#		                else:
#					#self.log.broadcast(ptolemy.data.StringToken("horario "))
#					return self.walkhorario()





	def whereImGoing(self):
		lx= float(self.lex)
		ly= float (self.ley)
		lz= float(self.lez)
		myId = self.mId
		distance = 2
		if (myId == "0"): # Im the leader
			return (0, 0)
		elif (myId == "1"):
			return lx -distance , ly - distance
		elif (myId == "2"):
			return lx + distance , ly  + distance
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
		self.linear.broadcast(ptolemy.data.DoubleToken(linear))
		self.angular.broadcast(ptolemy.data.DoubleToken(angular))
		return
