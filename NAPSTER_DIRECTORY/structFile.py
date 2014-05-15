class structFile:
    def __init__(self, nome, md5, idsess):
		self.idsess=[]
		self.nome = nome
		self.md5 = md5
		self.idsess.append(idsess)
		self.total = 0
		print "		AGGIUNTO ---> ", self.nome
		print "		INVIATO DA ----> ", self.idsess
