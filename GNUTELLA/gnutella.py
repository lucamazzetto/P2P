#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#gnutella

import socket,stat,sys,hashlib,os,threading,thread,time,re
import random 
import string 
mioIP="fd00:0000:0000:0000:22c9:d0ff:fe47:70a3"
PortaQuery="3000"
PortaDownload="3001"
listaPKTIDnear={}
gestioneRisposte={} #oggetto della classe threadRisposte
listaVicini={} #lista degli ip e porte dei vicini
vicini={} #thread per fare query ai vicini
indiceParametri=0
indiceLista=2
parametri={}
listaPKTID={}  #lista dei PKTID ricevuti nel pacchetto query
indicePKTID=0
indicePKTIDnear=0
fileCondivisi={}
PKTIDmio={}
fileTrovati={}
spegniRicerca=0
#classe che contiene i pacchetti ricevuti dalla query 
class IDpacchetti:
	PKTID=''
	TEMPO=''
	def __init__(self,PKTID,TEMPO):		
		self.PKTID=PKTID
		self.TEMPO=TEMPO
		
#CLASSE che contiene i filemd5 e filename che condividiamo
class FileCondivisi:
	PERCORSO=''
	FILEMD5=''
	def __init__(self,PERCORSO, FILEMD5):		
		self.PERCORSO=PERCORSO
		self.FILEMD5=FILEMD5
				
#classe che contiene ip e porta dei vicini
class Vicini:
	IP=''
	PORTA=''
	# The constructor
	def __init__(self,IP, PORTA):		
		self.IP=IP
		self.PORTA=PORTA
		
#-------------------------------------------------------------------------------------------------------------

#CLASSE SALVA PARAMETRI: MEMORIZZA I PARAMETRI DI RITORNO DALLA RICERCA PER POTERLI UTILIZZARE NEL DOWLOAD
class SalvaParametri:	
	IP=''
	PORTA=''
	FILEMD5=''
	FILENAME=''
	# The constructor
	def __init__(self,IP, PORTA, FILEMD5,FILENAME):		
		self.IP=IP
		self.PORTA=PORTA
		self.FILEMD5=FILEMD5
		self.FILENAME=FILENAME
#--------------------------------------------------------------------------------------	
#FUNZIONI
	
def creaIP(ip):
	l=ip.split(":")
	i=0
	while i<len(l):
		l[i]="0"*(4-len(l[i]))+l[i]
		i=i+1
	
	return str(l[0])+":"+str(l[1])+":"+str(l[2])+":"+str(l[3])+str(l[4])+":"+str(l[5])+":"+str(l[6])+":"+str(l[7])
	
	
def creaPorta(dim,argomento):
	if len(argomento) < dim :
		differenza=dim-len(argomento)
		i=0
		while i<differenza:
			argomento="0"+argomento
			i=i+1
	return argomento
#stampa una lista
def stampa(l): 
	i=0
	while i<len(l):
		if l[i].PKTID!='' and l[i].PKTID!=0:
			print l[i].PKTID,l[i].TEMPO
		i=i+1
		
def stampaVicini(l):
	i=0
	while i<len(l):
		print "IP vicino: ",l[i].IP,"PORTA vicino: ", l[i].PORTA
		i=i+1
#Funzione scrivi file di log
def scriviLog(Str):
	logTime = time.localtime(time.time())
	ora=time.strftime("%d/%m/%Y %H:%M:%S", logTime)
	flog=open ('./Log.txt', 'a')
	flog.write (ora+"    ----     "+Str+"\n")
	flog.close()

#cancella pacchetti scaduti mettendo a 0 il tempo e nessun valore al pktid	
def cancellaPacchettiScaduti(lista,tempo):
	i=0
	while i<len(lista):
		if lista[i].TEMPO!=0:
			if tempo-lista[i].TEMPO >= 150:
				lista[i].TEMPO=0
				lista[i].PKTID=''
		i=i+1
	
	
def cancellaVicini(valore_da_cancellare,lista):
	i=valore_da_cancellare
	while(i<len(lista)-1):
		lista[i]=lista[i+1]
		i=i+1
		
	del lista[len(lista)-1]
	return lista	
#Funzione ricerca file
def cercaFile(Ricerca):
	lista=(os.listdir('./immagine'))
	Ricerca=Ricerca.strip()
	p = re.compile(Ricerca,re.IGNORECASE)
	file={}
	i=0
	k=0
	while i<len(lista) :
		m = p.search(lista[i]) 
		if m:
			file[k]=lista[i]
			k=k+1		
		i=i+1
	return file
#funzione che salva tutti i filename e i filemd5 che condividiamo
def SalvaFile():
	
	lista=(os.listdir('./immagine')	)
	i=0
	while i <len(lista):
		percorso="./immagine/"+lista[i]
		filemd5=creazioneFilemd5(percorso)
		fileCondivisi[i]=FileCondivisi(percorso,filemd5)
		i=i+1
#FUNZIONE confronta file md5: quando sono uguali restituisco il percorso
def trovaPercorso(lista,filemd5):
		i=0
		while i<len(lista):
			if lista[i].FILEMD5==filemd5:
				return lista[i].PERCORSO
				break
			else :
				i=i+1
		print "File md5 non compatibile..."
		exit()	
def ricercaPKTID(PKTID,lista):
	i=0
	while i < len(lista):
		if lista[i].PKTID==PKTID:  #il pKTID è presente
			return 0
		i=i+1
	return 1

def ricercaVicini(IP,Porta,lista):
	i=0
	while i < len(lista):
		if lista[i].IP==IP and lista[i].PORTA==Porta:  #se l'ip e la porta sono presenti
			return 0
		i=i+1
	return 1		
	
#----------------------------------------------------------------------
#CONTROLLO DIMENSIONE DELL'ARGOMENTO DEL PACCHETTO PACCHETTO
def controllaArgomentoStringa(dim,argomento):	
	if len(argomento) > dim :
		print "FUNZIONE controllaArgomentoStringa-->Errore argomento troppo lungo.L'argomento viene troncato"
		argomento=argomento[0:dim]
	if len(argomento) < dim :
		differenza=dim-len(argomento)
		i=0
		while i<differenza:
			argomento=argomento+" "
			i=i+1
	return argomento
def controllaDimensione(TTL):
	if len(TTL)<2:
		TTL='0'+TTL
	return TTL

def controlla16B(dim,argomento):
	if len(argomento) > dim :
		print "FUNZIONE controlla16B-->Errore argomento troppo lungo."
		exit()
	if len(argomento) < dim :
		print "Errore argomento troppo corto."
		exit()
	return argomento
	
def creazioneFilemd5(percorsoFile):
	Filemd5=hashlib.md5(open(percorsoFile,"rb").read()).digest()
	Filemd5=controlla16B(16,Filemd5)
	return Filemd5
#-------------------------------------------------------------------
def generaPKTID(N):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N)) 	
	
#------------------------------------------------------------------
def creazioneSocket(IP,Porta):
	#apertura socket	
	peer_socket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
	peer_socket.connect((IP,int(Porta)))
	return peer_socket
	
def query(PKTID,mioIP,PortaQuery,TTL,Ricerca):
	
	Ricerca=controllaArgomentoStringa(20,Ricerca)
	pacchetto="QUER"+PKTID+mioIP+PortaQuery+TTL+Ricerca
	return pacchetto

def near(PKTID,mioIP,PortaQuery,TTL):	
	pacchetto="NEAR"+PKTID+mioIP+PortaQuery+TTL
	return pacchetto
	
def anea(PKTID,mioIP,PortaQuery):	
	pacchetto="ANEA"+PKTID+mioIP+PortaQuery
	#print pacchetto
	return pacchetto
	
def aque(PKTID,IP,P,Filename):
	percorso="./immagine/"+Filename
	Filemd5=creazioneFilemd5(percorso)	
	Filemd5=controlla16B(16,Filemd5)
	Filename=controllaArgomentoStringa(100,Filename)
	pacchetto="AQUE"+PKTID+IP+P+Filemd5+Filename	
	return pacchetto
	
def download(IPP2P,PortaP2P,Filemd5):  #invio la richiesta per scaricare un file
	#apertura socket con altro peer	
	socketD=creazioneSocket(IPP2P,PortaP2P)	
	Filemd5=controlla16B(16,Filemd5)
	pacchetto="RETR"+Filemd5
	#invio pacchetto al peer
	socketD.send(pacchetto)
	return 	socketD
#------------------------------------------------------------------
#Thread per gestire dowload file --> per ogni richiesta ricevuta crea un thread client
class server(threading.Thread):

	# The IP address
	ip=""
	# The number of max connections
	maxconn=5
	# The main socket
	mainsocket=None
	# Tells if the main socket is ok
	mainready=False
	# The client threads
	clients={}	
	def __init__(self):
		threading.Thread.__init__(self)
	
	# Initialize the main socket
	def run(self):
		# Create the socket
		try:
			mainsocket=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			
			
			#print ('la socket è creata.')
		except:
			self.log('errore socket')
			return False
		try:
			mainsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except:
			self.log('errore sockopt.')
			return False
		mainsocket.bind((mioIP, int(PortaDownload)))
		#try:
			#mainsocket.bind((mioIP, int(PortaDownload)))
	#	except:
	#		print mioIP,PortaDownload
	#		self.log('errore bind.')
	#		return False
		# Listen on it
		try:
			mainsocket.listen(self.maxconn)
			#print ('la socket è in ascolto.')
		except:
			self.log('Cannot listen on the socket.')
			return False
				

		# Share it with the class
		mainsocket=mainsocket		
		mainready=True
		while 1:
			#print "sono dentro a while 1"
			try:
				if not mainready:
					raise Exception()
					return False

				# Wait for a connection
				#inputready,outputready,ex = select.select([mainsocket],[],[],2)
				#for i in inputready:
				(conn, addr) = mainsocket.accept()
				
					# Build the id for the connection
				cid=addr[0]					
				self.log('Connected by ' + cid)
				# Init the client					
				self.clients[cid]=client(cid, conn,self)
				self.clients[cid].start()
			except KeyboardInterrupt:
				print('KeyboardInterrupt received. Closing the server.')
				break	
					
			except:
				break

	# Close the main socket
	def closeMain(self):
		if not self.mainready:
			return True
		try:
			self.mainsocket.close()
			return True
		except:
			self.log('Cannot close main socket')
			return False

	# Close the clients
	def closeClients(self):
		# Send the closing signal to clients
		for i in self.clients:
			# Don't destroy clients or the for will complain
			self.clients[i].close(True)

		# Reset the clients dict
		self.clients={}
	# Log the errors
	def log(self, msg):
		print(msg)
	
#thread per inviare il file richiesto--> riceve pacchetto RETR
class client(threading.Thread):
	# The id of the client
	id=''
	# The connection
	socket=''	
	# Can receive?
	receive=1
	# The server instance
	server=None
	# The constructor
	def __init__(self, id, socket, server):
		threading.Thread.__init__(self)
		self.id=id
		self.socket=socket
		self.server=server		
		
	# The running method
	def run(self):
		socketClient=self.socket		
		identificativo=socketClient.recv(4) 
		if not identificativo:
			print "ERRORE RICEZIONE PACCHETTO RETR"
			sys.exit(1)			
		if identificativo !="RETR":
			print "ERRORE RICEZIONE IDENTIFICATIVO RETR"			
		Filemd5=socketClient.recv(16)	
		Filemd5=controlla16B(16,Filemd5)		
		percorsoFile=trovaPercorso(fileCondivisi,Filemd5)
		fd = os.open(percorsoFile,os.O_RDONLY)		
		filesize = os.fstat(fd)[stat.ST_SIZE]		
    		nChunk=filesize/4096    
		
		if (filesize%4096) !=0:  #se resto=0 allora i valori sono divisibili altrimenti aggiungiamo un valore
			nChunk=nChunk+1	
		nChunk=str(nChunk).zfill(6)
		   		
		pacchetto="ARET"+nChunk
		#print pacchetto
		print "Trasferimento in corso.."
		i=1
		while i<= int(nChunk):
			buf=os.read(fd,4096) #legge dal file				
			if not buf: break
			lBuf=len(buf)
			lBuf=str(lBuf).zfill(5)	
			pacchetto=pacchetto+lBuf+buf   #costruisco il pacchetto
			i=i+1	
		print "Trasferimento effettuato!!"			
		socketClient.send(pacchetto) 
		os.close(fd)
		time.sleep(50)		
		socketClient.close()		
	def close(self, nodestroy=False):
		self.log('Disconnetting')
		self.receive=0
		self.socket.close()

		# Destroy from the server this client?
		if not nodestroy:
			del self.server.clients[self.id]

	# Log. By default it uses the server class
	def log(self, msg):
		self.server.log('Client '+self.id+': '+msg)
		
#-------------------------------------------------------------------------------------------
class threadRicerca(threading.Thread): #thread che manda pacchetto query a tutti i vicini
	# The IP address
	ip=""
	porta=""
	socketQuery=None
	pacchetto=''
	i=''
	# The client threads
	clients={}	
	def __init__(self,IP,Porta,pacchetto,i):
		threading.Thread.__init__(self)
		self.ip=IP
		self.porta=Porta
		self.pacchetto=pacchetto	
		self.i=i
		#self.socketQuery=socket
	
	def run(self):
		# Create the socket
		global listaVicini
		try:
			self.socketQuery=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.socketQuery.connect((self.ip, int(self.porta)))
			#print ('la socket è creata.')
		except:
			self.log("Il vicino noto "+self.ip+" si è scollegato...Verrà cancellato")
			listaVicini=cancellaVicini(self.i,listaVicini)

			return False	
		self.socketQuery.send(self.pacchetto)
		self.socketQuery.close()
	# Log the errors
	def log(self, msg):
		print(msg)

#--------------------------------------------------------------------------------------
#thread che resta sempre in ascolto per 300sec--> ad ogni richiesta ricevuta crea un thread threadRisposte
class ThreadAscolto(threading.Thread):
	ip=""
	porta=""
	maxconn=5	
	socketACK=''
	def __init__(self,Porta):
		threading.Thread.__init__(self)		
		self.porta=Porta		
	def run(self):
		# Create the socket
		try:
			self.socketACK=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.socketACK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socketACK.bind((mioIP, int(self.porta)))
			#print ('la socket è creata.')
		except:
			self.log('Cannot bind the socketACK.')
			return False

		# Listen on it
		try:
			self.socketACK.listen(self.maxconn)
			#print ('la socket è in ascolto.')
		except:
			self.log('Cannot listen on the socket.')
			return False			

		# Share it with the class
		self.socketACK.settimeout(150)
		while 1:
			
			try:				
				(conn, addr) = self.socketACK.accept()
				cid=addr[0]
				#print "cid: ",cid									
				gestioneRisposte[cid]=threadRisposte(cid, conn,self)
				gestioneRisposte[cid].start()
			except socket.timeout:
				print "Tempo scaduto.....cancellazione pacchetti in corso.."	
				tempo=time.time()
				cancellaPacchettiScaduti(listaPKTID,tempo)
				cancellaPacchettiScaduti(listaPKTIDnear,tempo)
				cancellaPacchettiScaduti(PKTIDmio,tempo)
				print
				print "eccezione"
				print "tempo ",tempo
				#print "lunghezza listaPKTID ",len(listaPKTID)
				print "Tempi dopo eccezione ",stampa(listaPKTID)
				print 
				#cancellaPacchettiScaduti(PKTIDmio,tempo)
				self.socketACK.settimeout(150)
				#client_socket.send("tempo scaduto")		
	def log(self, msg):
		print(msg)
	def closeSocketACK(self):
		try:
			self.socketACK.close()
			return True
		except:
			self.log('Cannot close socketACK')
			return False
	
									
#thread che gestisce i pacchetti QUER, AQUE, ANEA
class threadRisposte(threading.Thread): 
	# The id of the client
	id=''
	# The connection
	socketACK=None	
	receive=1
	# The server instance
	server=None
	# The constructor
	def __init__(self, id, socket, server):
		threading.Thread.__init__(self)
		self.id=id
		self.socketACK=socket
		self.server=server		
		

	# The running method
	def run(self):	
		global indiceParametri
		global indiceLista
		global indicePKTID
		global indicePKTIDnear
		global listaPKTID
		global listaPKTIDnear
		global listaVicini
		global spegniRicerca
		identificativo=self.socketACK.recv(4)#146B per ogni riga
		if not identificativo:
			print "ERRORE RICEZIONE PACCHETTO"
			sys.exit(1)					
		if identificativo !="AQUE" and identificativo !="NEAR" and identificativo !="QUER" and identificativo !="ANEA":
			print "ERRORE RISPOSTA IDENTIFICATIVO"
		if identificativo =="AQUE":
			if spegniRicerca==0:
				PKTID=self.socketACK.recv(16)
				PKTID=controlla16B(16,PKTID)
				if(ricercaPKTID(PKTID,PKTIDmio)==0):
					IPparametro=self.socketACK.recv(39)
					IPparametro=controllaArgomentoStringa(39,IPparametro)
					Portaparametro=self.socketACK.recv(5)
					Portaparametro=controllaArgomentoStringa(5,Portaparametro)
					Filemd5=self.socketACK.recv(16)
					Filemd5=controlla16B(16,Filemd5)
					Filename=self.socketACK.recv(100)
					Filename=Filename.strip();
					parametri[indiceParametri]=SalvaParametri(IPparametro,Portaparametro,Filemd5,Filename)
					stampa=str(indiceParametri)+") "+ Filename+" "+IPparametro+" "+Portaparametro
					print stampa, " -->Pacchetto AQUE ricevuto dal peer ", self.id
					indiceParametri=indiceParametri+1					
				
				else:
					print "Il pacchetto AQUE ricevuto non corrisponde a una nostra richiesta."
					
		if identificativo =="ANEA":
			PKTID=self.socketACK.recv(16)
			PKTID=controlla16B(16,PKTID)
			IPparametro=self.socketACK.recv(39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=self.socketACK.recv(5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			if ricercaVicini(IPparametro,Portaparametro,listaVicini) ==1:				
				listaVicini[indiceLista]=Vicini(IPparametro,Portaparametro)
				indiceLista=indiceLista+1
			print "Pacchetto ANEA ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro
			
			
		if identificativo =="NEAR":
			ip=creaIP(self.id)
			PKTID=self.socketACK.recv(16)
			PKTID=controlla16B(16,PKTID)
			IPparametro=self.socketACK.recv(39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=self.socketACK.recv(5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			TTL=self.socketACK.recv(2)
			TTL=controllaDimensione(TTL)
			if ricercaPKTID(PKTID,listaPKTIDnear)==1 : #pktid non esistente
				listaPKTIDnear[indicePKTIDnear]=IDpacchetti(PKTID,time.time())
				indicePKTIDnear=indicePKTIDnear+1
				print "Pacchetto NEAR ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",TTL
				pacchettoANEA=anea(PKTID,mioIP,PortaQuery)
				v=threadRicerca(IPparametro,Portaparametro,pacchettoANEA,-1) #ritrasmetto il pacchetto
				v.start() 	
				scriviLog("Invio "+pacchettoANEA+" Vicino "+IPparametro+":"+Portaparametro)		
				if(int(TTL)>1):  #invio di nuovo il pacchetto
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)	
					pacchetto=near(PKTID,IPparametro,Portaparametro,TTL)						
					i=0
					while i< len(listaVicini): #indiceLista è l'indice per scorrere la lista dei vicini 
						if(listaVicini[i].IP != IPparametro and listaVicini[i].IP !=ip):
						#if((listaVicini[i].IP != IPparametro and listaVicini[i].PORTA != Portaparametro) and listaVicini[i].IP !=ip): #controllo per non rinviare il pacchetto a chi me lo ha inviato
							vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i) #ritrasmetto il pacchetto
							vicini[i].start()	
							scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)													
						i=i+1					
			else:
				scriviLog("!!!!SCARTATO Pacchetto NEAR  "+ self.id+" : "+PKTID+" "+IPparametro+" "+Portaparametro+" "+TTL)
		if identificativo =="QUER":
			ip=creaIP(self.id)
			#print "ip: ",ip
			PKTID=self.socketACK.recv(16)
			PKTID=controlla16B(16,PKTID)
			#if ricercaPKTID(PKTID,listaPKTID)==1 : #pktid non esistente
			#listaPKTID[indicePKTID]=IDpacchetti(PKTID,time.time())
			#indicePKTID=indicePKTID+1
					
			IPparametro=self.socketACK.recv(39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=self.socketACK.recv(5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			TTL=self.socketACK.recv(2)
			TTL=controllaDimensione(TTL)
			Ricerca=self.socketACK.recv(20)
			Ricerca=controllaArgomentoStringa(20,Ricerca)	
			pacchettoR=identificativo+PKTID+IPparametro+Portaparametro+TTL+Ricerca
			#print "Pacchetto QUER ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",Ricerca," ",TTL	
			if ricercaPKTID(PKTID,listaPKTID)==1 : #pktid non esistente
				print "Pacchetto QUER ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",Ricerca," ",TTL	
				listaPKTID[indicePKTID]=IDpacchetti(PKTID,time.time())
				indicePKTID=indicePKTID+1		
				if(int(TTL)>1):  #invio di nuovo il pacchetto
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)						
					pacchetto=query(PKTID,IPparametro,Portaparametro,TTL,Ricerca)
					i=0
					while i< len(listaVicini): #indiceLista è l'indice per scorrere la lista dei vicini 		
						#print "vicino ",listaVicini[i].IP,listaVicini[i].PORTA
						if(listaVicini[i].IP != IPparametro and listaVicini[i].IP != ip): #controllo per non rinviare il pacchetto a chi me lo ha inviato
							vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i) #ritrasmetto il pacchetto
							vicini[i].start() 	
							scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)							
						i=i+1
			
				fileTrovati=cercaFile(Ricerca) #cerco il file nella mia cartella dopo aver propagato la query			
				if len(fileTrovati) >0: #abbiamo il file richiesto--> lo diciamo al nodo interessato				
					#inviamo solo il primo file trovato	
					k=0
					while k< len(fileTrovati): 
						try:
							socketAQUE=creazioneSocket(IPparametro,Portaparametro)							
						except:
							self.log('Cannot connect the socketAQUE.')
							return False	
						#filename=controllaArgomentoStringa(100,fileTrovati[k])
						pacchetto=aque(PKTID,mioIP,PortaDownload,fileTrovati[k])	
						socketAQUE.send(pacchetto)	
						k=k+1						
						socketAQUE.close()
						scriviLog("Invio "+pacchetto+" Vicino "+IPparametro+":"+Portaparametro)							
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)			
		self.socketACK.close()
		
					
	def close(self, nodestroy=False):
		self.log('Disconnetting')
		self.receive=0
		self.socketACK.close()

		# Destroy from the server this client?
		if not nodestroy:
			del self.server.gestioneRisposte[self.id]

	# Log. By default it uses the server class
	def log(self, msg):
		self.server.log('Client '+self.id+': '+msg)					
#-----------------------------------------------------------------------------------------

scriviLog("NUOVA SESSIONE")
IP=raw_input("Inserisci IP vicino 1: ") 
Porta=raw_input("Inserisci Porta vicino 1: ") 
Porta=creaPorta(5, Porta)
IP=creaIP(IP) 
listaVicini[0]=Vicini(IP,Porta)
scriviLog("Primo vicino: "+IP+":"+Porta)

IP=raw_input("Inserisci IP vicino 2: ") 
Porta=raw_input("Inserisci Porta vicino 2: ") 
Porta=creaPorta(5, Porta)
IP=creaIP(IP)  
listaVicini[1]=Vicini(IP,Porta)
scriviLog("Secondo vicino: "+IP+":"+Porta)
SalvaFile() #salvo i filemd5 e filename che voglio condividere
j=0
#faccio partire il thread del server per stare in ascolto di possibili download
s=server()
s.start()
#faccio partire il thread di ascolto generale 
ascolto=ThreadAscolto(PortaQuery)
ascolto.start()
scriviLog("Threads partiti")
#menu:
while 1:
		print
		print
		print "OPERAZIONI POSSIBILI:"		
		print "1. ricerca file;"
		print "2. ricerca vicini;"
		print "3. download file;"
		print "4. stampa vicini;"
		print "5. stampa PKTID;"
		print "6. esci."
		
		
		scelta=raw_input("Numero operazione: \n")

		
		if scelta=="1": #ricerca file
			spegniRicerca=0
			parametri={}
			indiceParametri=0
			TTL=raw_input("Inserisci Time to live (TTL): ")
			TTL=controllaDimensione(TTL)
			Ricerca=raw_input("Inserisci la stringa di ricerca: ") #il controllo della lunghezza di Ricerca è dentro alla funzione query			
			PKTID=generaPKTID(16)
			PKTID=controlla16B(16,PKTID)
			PKTIDmio[j]=IDpacchetti(PKTID,time.time())  #ci salviamo il PKTID che mandiamo
			j=j+1
			pacchetto=query(PKTID,mioIP,PortaQuery,TTL,Ricerca) #costruisco il pacchetto QUER
			i=0			
			while i< len(listaVicini):		#inviamo il pacchetto QUER a tutti i vicini			
				vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i)
				vicini[i].start()
				scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)
				i=i+1				
				
		if scelta=="2" :#ricerca vicini
			indiceLista=2
			TTL=raw_input("Inserisci Time to live (TTL) per i vicini: ")
			TTL=controllaDimensione(TTL)
			try:
				socketVicino1=creazioneSocket(listaVicini[0].IP,listaVicini[0].PORTA)	
				socketVicino2=creazioneSocket(listaVicini[1].IP,listaVicini[1].PORTA)
				PKTID=generaPKTID(16)
				PKTID=controlla16B(16,PKTID)	
				pacchetto=near(PKTID,mioIP,PortaQuery,TTL) #creazione pacchetto NEAR
				socketVicino1.send(pacchetto)
				socketVicino2.send(pacchetto)	
				socketVicino1.close()
				socketVicino2.close()	
			except:
				print "Il nodo si è disconnesso."
			
		
			
		if scelta=="3": #download file			
			print "download file in corso....."
			loc="./fileScaricati/"
			recvfn	= raw_input("Inserisci il nome del file.estensione per salvare: ")
			#loc = raw_input("In che cartella salvare? ")
			if loc[-1] != os.sep: loc += os.sep
			fd = os.open(loc+recvfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0600)			
			indice=raw_input("Inserisci indice del file da scaricare: ")
			spegniRicerca=1
			IP=parametri[int(indice)].IP
			Porta=parametri[int(indice)].PORTA
			Filemd5=parametri[int(indice)].FILEMD5
			#Filename=parametri[int(indice)].FILENAME			
			socketD=download(IP,Porta,Filemd5) #creazione pacchetto RETR
			#risposta al download dal peer
			risposta=socketD.recv(10) #impostare bene le dimensioni
			if not risposta:
				print "ERRORE RICEZIONE PACCHETTO DOWNLOAD DAL PEER"
				sys.exit(1)
			identificativo=risposta[0:4]
			#print identificativoPeer
			if identificativo !="ARET":
				print "ERRORE RISPOSTA DOWNLOAD PEER"
			nChunk=int(risposta[4:10])  			
			conta=1	
			while conta <= nChunk:
				lenChunk=socketD.recv(5)
				while len(lenChunk)<5:
					lenChunk=lenChunk+socketD.recv(1)
				lenChunk=int(lenChunk)	
				
				data=socketD.recv(lenChunk)
				while len(data)<lenChunk:
					data=data+socketD.recv(1)
				os.write(fd, data)	
				conta=conta+1			
			print "Il file è stato salvato con successo!"			
			os.close(fd)			
			socketD.close() 
			
		if scelta=="4":#stampo la lista dei vicini
			stampaVicini(listaVicini)
			
		if scelta=="5":
			stampa(listaPKTID)
		
		if scelta=="6":
			s.closeMain()#chiudiamo la socket del server
			ascolto.closeSocketACK()#chiudiamo la socket del threadAscolto
			print "...FINE...."
			break
			
