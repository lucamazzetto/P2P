#NAPSTER GRUPPO 03
# -*- coding: UTF-8 -*-

#guerra 	fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
#mazzetto	fd00:0000:0000:0000:8896:7854:b792:1bd1
#natali 	fd00:0000:0000:0000:7ed1:c3ff:fe76:362a

class structFile:
    def __init__(self, nome, md5, idsess):
		self.idsess=[]										#lista peer che hanno il file
		self.nome = nome									#nome file
		self.md5 = md5										#md5 del file
		self.idsess.append(idsess)							#aggiunta di un peer alla lista peer
		self.total = 0										#numero di download
		print "		AGGIUNTO ---> ", self.nome
		print "		INVIATO DA ----> ", self.idsess
