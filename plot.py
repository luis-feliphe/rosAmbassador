import sys
filei = sys.argv[1]
tipo = sys.argv [2]
isMedia = False
if (tipo == "media"):
	isMedia = True
arquivo = open (filei, "r")
valores = arquivo.readlines()
arquivo.close()
listax = []
listay = []
somatorioTempo = 0
contador = 1
for i in valores:
	x , y = i.replace("\n", "").replace(".0", "").split(":")
	listax.append(int(x))
	somatorioTempo+= int (y)
	if (isMedia):
		listay.append(somatorioTempo/float(contador))
	else:
		listay.append(int(y))
	contador+=1

	
import numpy 
dp = numpy.array(listay)
print ("desvio padrao= "+ str(numpy.std(dp)))
print ("media = "+ str(numpy.mean(dp)))
import pylab
pylab.plot(listax, listay)
pylab.xlabel('Iteracao')
pylab.ylabel('Tempo (ms)')
pylab.title('Tempo de resposta ao longo das Iteracoes') 
pylab.show()
#print float(sum(tempo)) / len (tempo)
	
	
#mya.terminate()
#rtia.resignFederationExecution(hla.rti.ResignAction.DeleteObjectsAndReleaseAttributes)
#print("Done.")
