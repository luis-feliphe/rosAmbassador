arquivo = open ("resultadoSimulacao.txt", "r")
valores = arquivo.readlines()
arquivo.close()
listax = []
listay = []
for i in valores:
	x , y = i.replace("\n", "").replace(".0", "").split(":")
	listax.append(int(x))
	listay.append(int(y))

	
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
