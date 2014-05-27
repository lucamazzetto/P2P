class structFile:
    def __init__(self, nome, randomId, lenFile, lenPart, partList, idsess):
		self.idsess=[]
		self.partList=[]
		self.nome = nome
		self.randomId = randomId
		self.lenFile = lenFile
		self.lenPart = lenPart
		self.idsess.append(idsess)
		self.partList.append(partList)
		self.total = 0
		print "		AGGIUNTO ---> ", self.nome
		print "		INVIATO DA ----> ", self.idsess
