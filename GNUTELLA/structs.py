import random
import string

# Classe per la gesione dei pktId
class structPktId:
    # costruttore
    def __init__(self, pktId,timeCreaz):
		self.pktId = pktId
		self.timeCreaz = timeCreaz
		# stampa un messaggio
		#print "		Aggiunto file: ", self.nome
		#print "		inviato da: ", self.idsess
		
		

		
class structNeigh:

	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		

class structRis:

	def __init__(self, pktId, ip, port, md5, nameF ):
		self.pktId = pktId
		self.md5 = md5
		self.nameF = nameF
		self.ip = ip
		self.port = port


# funzione che crea un id di volta in volta diverso in modo random	
def pktId():
	id = ""
	letter = []
	letters =["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
	for i in range(1,17):
		id=id+letters[int(random.random() * (len(letters)-1))]
	return str(id)
