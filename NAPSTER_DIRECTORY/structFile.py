# Classe per la gestione dei file all'interno della directory
class structFile:
    # costruttore
    def __init__(self, nome, md5, idsess):
		self.idsess=[]
		self.nome = nome
		self.md5 = md5
		self.idsess.append(idsess)
		self.total = 0
		# stampa un messaggio
		print "		Aggiunto file: ", self.nome
		print "		inviato da: ", self.idsess
