#GNUTELLA GRUPPO 03
# -*- coding: UTF-8 -*-

#guerra 	fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
#mazzetto	fd00:0000:0000:0000:8896:7854:b792:1bd1
#natali 	fd00:0000:0000:0000:7ed1:c3ff:fe76:362a

import socket    		#libreria per socket
import string           #manipolazione di stringhe
import thread           #libreria per thread
import sys              #libreria per cartelle
import re               #libreria per espressioni
import stat 			#libreria per operare con i path
import hashlib 			#libreria per md5
import os				#libreria per operare con OS
import threading		#libreria per threading
import thread 			#libreria per threading
import time 			#libreria per timeout
import random 			#libreria per generazione numeri casuali

#Definizione delle variabili utilizzate
mioIP="fd00:0000:0000:0000:22c9:d0ff:fe47:70a3"
PortaQuery="03000"
PortaDownload="03001"
listaPKTIDnear={} 													#lista PKTID dei vicini
gestioneRisposte={} 												#oggetto della classe threadRisposte
listaVicini={}														#lista IPv6 e porte dei vicini
vicini={} 															#lista thread per fare query ai vicini
indiceParametri=0 													
indiceLista=1
parametri={} 														#lista dei parametri salvati per il download
listaPKTID={}  														#lista dei PKTID ricevuti nel pacchetto query
indicePKTID=0
indicePKTIDnear=0 													
fileCondivisi={} 													#Lista file condivisi
PKTIDmio={}															#PKTID pacchetti mandati da me
fileTrovati={} 														#Lista file trovati
spegniRicerca=0 													#Termina la ricerca

#Classe per salvare PKTID e tempo dei pacchetti ricevuti in query
class IDpacchetti:
	PKTID=''
	TEMPO=''
	def __init__(self,PKTID,TEMPO):		
		self.PKTID=PKTID
		self.TEMPO=TEMPO
		
#Classe per salvare md5 e percorso dei file che condividiamo
class FileCondivisi:
	PERCORSO=''
	FILEMD5=''
	def __init__(self,PERCORSO, FILEMD5):		
		self.PERCORSO=PERCORSO
		self.FILEMD5=FILEMD5
				
#Classe con contiene i vicini con loro IPv6 e porta
class Vicini:
	IP=''
	PORTA=''
	def __init__(self,IP, PORTA):		
		self.IP=IP
		self.PORTA=PORTA
		
#Classe per poter salvare i dati che mi ritornano con la ricerca
class SalvaParametri:	
	IP=''
	PORTA=''
	FILEMD5=''
	FILENAME=''
	def __init__(self,IP, PORTA, FILEMD5,FILENAME):		
		self.IP=IP
		self.PORTA=PORTA
		self.FILEMD5=FILEMD5
		self.FILENAME=FILENAME

#Funzione per la creazione dell'IPv6 per esteso a partire da uno contratto
def creaIP(ip):
	l=ip.split(":")
	diff=8-len(l)
	n="0000:0000:0000:0000:0000:0000:0000:0000"
	v=n.split(":")
	i=0
	k=0
	while i<len(l):
		
		if l[i]!='':
			v[k]=l[i]
			i=i+1
			k=k+1
		else:
			i=i+1
			k=k+diff+1		
	return str(v[0])+":"+str(v[1])+":"+str(v[2])+":"+str(v[3])+":"+str(v[4])+":"+str(v[5])+":"+str(v[6])+":"+str(v[7])

#Funzione per l'eliminazione degli asterischi dalla stringa di ricerca
def elimina_asterischi(stringa):
        ritorno = ""
        ritorno2 = ""
        lettera = False
        lettera2 = False
        for i in range (0, len(stringa)):
            if(stringa[i] != "*" or lettera == True):
                ritorno = ritorno + stringa[i]
                lettera = True
       
        ritorno = ritorno[::-1]									#rovescio la stringa per cancellare quelli a destra
    
        for i in range (0,len(ritorno)):
            if(ritorno[i]!="*" or lettera2==True):
                ritorno2=ritorno2+ritorno[i]
                lettera2 = True
    
        return ritorno2[::-1]									#ri-rovescio la stringa per farla tornare giusta

	
#Funzione per fill con 0 del numero della porta
def creaPorta(dim,argomento):
	if len(argomento) < dim :
		differenza=dim-len(argomento)
		i=0
		while i<differenza:
			argomento="0"+argomento
			i=i+1
	return argomento

#Funzione per la Stampa di PKTID e tempo data una lista
def stampa(l): 
	i=0
	while i<len(l):
		if l[i].PKTID!='' and l[i].PKTID!=0:
			print l[i].PKTID,l[i].TEMPO
		i=i+1

#Funzione per la stampa della lista dei vicini
def stampaVicini(l):
	i=0
	while i<len(l):
		print "IP vicino: ",l[i].IP,"PORTA vicino: ", l[i].PORTA
		i=i+1

#Funzione per la scrittura del file di log
def scriviLog(Str):
	logTime = time.localtime(time.time())
	ora=time.strftime("%d/%m/%Y %H:%M:%S", logTime)
	flog=open ('./Log.txt', 'a')
	flog.write (ora+"    ----     "+Str+"\n")
	flog.close()

#Funzione per la cancellazione dei pacchetti scaduti
def cancellaPacchettiScaduti(lista,tempo):
	i=0
	while i<len(lista):
		if lista[i].TEMPO!=0:
			if tempo-lista[i].TEMPO >= 150:			#differenza tra tempo attuale e stamp di quando ho ricevuto il pacchetto
				lista[i].TEMPO=0
				lista[i].PKTID=''
		i=i+1
	
#Funzione per la cancellazione di un vicino dato l'indice nella lista
def cancellaVicini(valore_da_cancellare,lista):
	i=valore_da_cancellare
	while(i<len(lista)-1):							#se non è l'ultimo scorro la lista sovrascrivendo quello che voglio cancellare
		lista[i]=lista[i+1]
		i=i+1	
	del lista[len(lista)-1]							#cancello il vicino dalla lista se è l'ultimo o l'ultimo della lista se ho fatto lo scorrimento
	return lista

#Funzione per la ricerca del file
def cercaFile(Ricerca):
	lista=(os.listdir('./immagine'))				#ottengo la lista dei file in ./immagine
	Ricerca=Ricerca.strip()							#tolgo spazi prima e dopo la stringa
	p = re.compile(Ricerca,re.IGNORECASE)			#definisco cosa devo cercare e in che modo
	file={}											
	i=0
	k=0
	while i<len(lista) :							#ciclo sul contenuto di ./immagine per la ricerca della stringa di ricerca
		m = p.search(lista[i]) 						
		if m:										#se ho trovato qualcosa salvo il nome in file
			file[k]=lista[i]
			k=k+1		
		i=i+1
	return file 									#ritorno la lista di quello che ho trovato

#Funzione che salva tutti gli md5 e il percorso dei file che condividiamo (che sono in ./immagine)
def SalvaFile():
	lista=(os.listdir('./immagine')	)
	i=0
	while i <len(lista):
		percorso="./immagine/"+lista[i]
		filemd5=creazioneFilemd5(percorso)
		fileCondivisi[i]=FileCondivisi(percorso,filemd5)
		i=i+1

#Funzione che cerca un md5 nella lista dei file e se lo trova ritorna il percorso
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

#Funzione per il controllo se un PKTID è presente o meno nella lista (0 se presente, 1 se non presente)
def ricercaPKTID(PKTID,lista):
	i=0
	while i < len(lista):
		if lista[i].PKTID==PKTID:
			return 0
		i=i+1
	return 1

#Funzione per il controllo dato IP e porta si un peer se è un vicino (0 se vicino,1 se non vicino)
def ricercaVicini(IP,Porta,lista):
	i=0
	while i < len(lista):
		if lista[i].IP==IP and lista[i].PORTA==Porta:
			return 0
		i=i+1
	return 1		
	
#Funzione per il controllo se una stringa rispetta una lunghezza e per il fill con ' ' per farla diventare di lunghezza dim
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

#Funzione per il fill con 0 del TTL
def controllaDimensione(TTL):
	if len(TTL)<2:
		TTL='0'+TTL
	return TTL

#Funzione per il controllo dell'md5 se è 16B
def controlla16B(dim,argomento):
	if len(argomento) > dim :
		print "FUNZIONE controlla16B-->Errore argomento troppo lungo."
		exit()
	if len(argomento) < dim :
		print "Errore argomento troppo corto."
		exit()
	return argomento

#Funzione per la creazione dell'md5 di un file dato il percorso	
def creazioneFilemd5(percorsoFile):
	Filemd5=hashlib.md5(open(percorsoFile,"rb").read()).digest()
	Filemd5=controlla16B(16,Filemd5)
	return Filemd5

#Funzione per la generazione del PKTID di N caratteri
def generaPKTID(N):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N)) 	#definisco una scelta random di N elementi tra maiuscole e numeri	
	
#Funzione per la creazione della socket
def creazioneSocket(IP,Porta):
	peer_socket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
	peer_socket.connect((IP,int(Porta)))
	return peer_socket

#Funzione per la creazione del pacchetto QUER
def query(PKTID,mioIP,PortaQuery,TTL,Ricerca):
	Ricerca=controllaArgomentoStringa(20,Ricerca)
	pacchetto="QUER"+PKTID+mioIP+PortaQuery+TTL+Ricerca
	return pacchetto

#Funzione per la creazione del pacchetto NEAR
def near(PKTID,mioIP,PortaQuery,TTL):	
	pacchetto="NEAR"+PKTID+mioIP+PortaQuery+TTL
	return pacchetto

#Funzione per la creazione del pacchetto ANEA
def anea(PKTID,mioIP,PortaQuery):	
	pacchetto="ANEA"+PKTID+mioIP+PortaQuery
	return pacchetto

#Funzione per la creazione del pacchetto AQUE
def aque(PKTID,IP,P,Filename):
	percorso="./immagine/"+Filename
	Filemd5=creazioneFilemd5(percorso)	
	Filemd5=controlla16B(16,Filemd5)
	Filename=controllaArgomentoStringa(100,Filename)
	pacchetto="AQUE"+PKTID+IP+P+Filemd5+Filename	
	return pacchetto

#Funzione per la richiesta di download RETR con creazione della socket peer-peer e invio 	
def download(IPP2P,PortaP2P,Filemd5):
	socketD=creazioneSocket(IPP2P,PortaP2P)	
	Filemd5=controlla16B(16,Filemd5)
	pacchetto="RETR"+Filemd5
	socketD.send(pacchetto)
	return 	socketD

#Thread per la gestione dei download: per ogni richiesta di download crea un thread
class server(threading.Thread):

	ip=""												
	mainsocket=None
	mainready=False
	clients={}	
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		try:
			mainsocket=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			mainsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			mainsocket.bind((mioIP, int(PortaDownload)))
			mainsocket.listen(5)
		except:
			mainsocket = None
    		self.log("Errore mainsocket")
				
		mainready=True
		while 1:																#Ciclo infinito per l'ascolto
			(conn, addr) = mainsocket.accept()
			cid=addr[0]					
			self.log('Connessione da ' + cid)				
			self.clients[cid]=client(cid, conn, self)							#Salvo indirizzo e socket del peer in clients
			self.clients[cid].start()
			
	#Funzione per la chiusura della socket mainsocket
	def closeMain(self):
		try:
			self.mainsocket.close()
			return True
		except:
			self.log('Impossibile chiudere la socket')
			return False

	# Funzione per la chiusura delle connessioni dai peer
	def closeClients(self):
		for i in self.clients:
			self.clients[i].close(True)
		self.clients={}

	def log(self, msg):
		print(msg)
	
#Thread per l'invio di un file (risposta a RETR)
class client(threading.Thread):

	id=''
	socket=''
	receive=1
	server=None

	def __init__(self, id, socket, server):
		threading.Thread.__init__(self)
		self.id=id
		self.socket=socket
		self.server=server		
		
	def run(self):
		socketClient=self.socket		
		identificativo=socketClient.recv(4) 
		if not identificativo:										#Controllo se ho ricevuto RETR
			self.log("ERRORE RICEZIONE PACCHETTO RETR")
			sys.exit(1)			
		if identificativo !="RETR":
			self.log("ERRORE RICEZIONE IDENTIFICATIVO RETR")		
		Filemd5=socketClient.recv(16)	
		Filemd5=controlla16B(16,Filemd5)		
		percorsoFile=trovaPercorso(fileCondivisi,Filemd5)			#Trovo il file e lo divido in chunk da 4096
		fd = os.open(percorsoFile,os.O_RDONLY)		
		filesize = os.fstat(fd)[stat.ST_SIZE]		
    		nChunk=filesize/4096    
		
		if (filesize%4096) !=0:  									#Se dividibile per 4096 invio, altrimenti aggiungo un chunk
			nChunk=nChunk+1	
		nChunk=str(nChunk).zfill(6)									#Fill con 0 del numero dei chunk fino a 6
		   		
		pacchetto="ARET"+nChunk	
		self.log("Trasferimento in corso..")
		i=1
		while i<= int(nChunk):										#Ciclo per la costruzione dell'ARET
			buf=os.read(fd,4096)				
			if not buf: 
				break
			lBuf=len(buf)
			lBuf=str(lBuf).zfill(5)	
			pacchetto=pacchetto+lBuf+buf
			i=i+1	
		self.log("Trasferimento effettuato!!")			
		socketClient.send(pacchetto)								#Invio dell'ARET
		os.close(fd)
		time.sleep(50)		
		socketClient.close()

	#Funzione per la chiusura della socket		
	def close(self, nodestroy=False):
		self.log('Disconnessione')
		self.receive=0
		self.socket.close()
		if not nodestroy:
			del self.server.clients[self.id]						#Elimino client dalla lista client

	def log(self, msg):
		print(msg)

		
#Thread per l'invio dei pacchetti QUER ai vicini
class threadRicerca(threading.Thread):

	ip=""
	porta=""
	socketQuery=None
	pacchetto=''
	i=''
	clients={}

	def __init__(self,IP,Porta,pacchetto,i):
		threading.Thread.__init__(self)
		self.ip=IP
		self.porta=Porta
		self.pacchetto=pacchetto	
		self.i=i
	
	def run(self):
		global listaVicini
		try:																			#Creazione socket per QUER
			self.socketQuery=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.socketQuery.connect((self.ip, int(self.porta)))
		except:
			self.log("Il vicino noto "+self.ip+" si è scollegato...Verrà cancellato")
			listaVicini=cancellaVicini(self.i,listaVicini)

			return False	
		self.socketQuery.send(self.pacchetto)
		self.socketQuery.close()

	def log(self, msg):
		print(msg)

#Thread che resta in ascolto per 150ms, ad ogni richiesta crea un threadRichieste
class ThreadAscolto(threading.Thread):

	ip=""
	porta=""
	socketACK=''
	def __init__(self,Porta):
		threading.Thread.__init__(self)		
		self.porta=Porta		
	def run(self):
		try:																			#Creazione socket per ascolto
			self.socketACK=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.socketACK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socketACK.bind((mioIP, int(self.porta)))
			self.socketACK.listen(5)
		except:
			self.log('Impossibile utilizzare la socket')
			return False			

		self.socketACK.settimeout(150)
		while 1:																		#Accetto le connessioni sulla socket
			try:				
				(conn, addr) = self.socketACK.accept()
				cid=addr[0]								
				gestioneRisposte[cid]=threadRisposte(cid, conn,self)					#Delego a threadRisposte
				gestioneRisposte[cid].start()
			except socket.timeout:														#Se va in timeout la socket cancello i pacchetti
				print "TEMPO SCADUTO! Cancellazione pacchetti in corso..."	
				tempo=time.time()														#Salvo time stamp per controllare quali eliminare
				cancellaPacchettiScaduti(listaPKTID,tempo)
				cancellaPacchettiScaduti(listaPKTIDnear,tempo)
				cancellaPacchettiScaduti(PKTIDmio,tempo)
				print "Eccezione"
				print "Tempo ",tempo
				print "Tempi dopo eccezione ",stampa(listaPKTID)
				self.socketACK.settimeout(150)

	def log(self, msg):
		print(msg)

	#Funzione per la chiusura della socket
	def closeSocketACK(self):
		self.socketACK.close()
		return True

	
									
#Thread per la gestione dei pacchetti QUER, AQUE, ANEA
class threadRisposte(threading.Thread): 

	id=''
	socketACK=None	
	receive=1
	server=None

	def __init__(self, id, socket, server):
		threading.Thread.__init__(self)
		self.id=id
		self.socketACK=socket
		self.socketACK.setblocking(1)
		self.server=server		

	def run(self):	
		global indiceParametri
		global indiceLista
		global indicePKTID
		global indicePKTIDnear
		global listaPKTID
		global listaPKTIDnear
		global listaVicini
		global spegniRicerca
		global identificativo

		identificativo=self.socketACK.recv(4)									#Ricezione dell'identificativo del pacchetto

		if not identificativo:
			print "ERRORE RICEZIONE PACCHETTO"
			sys.exit(1)					
		if identificativo !="AQUE" and identificativo !="NEAR" and identificativo !="QUER" and identificativo !="ANEA":
			print "ERRORE RISPOSTA IDENTIFICATIVO"

		if identificativo =="AQUE":
			if spegniRicerca==0:
				PKTID=self.socketACK.recv(16)
				PKTID=controlla16B(16,PKTID)
				if(ricercaPKTID(PKTID,PKTIDmio)==0):										#Se il PKTId è il mio (ho mandato io la NEAR) salvo i parametri
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
			if ricercaVicini(IPparametro,Portaparametro,listaVicini) ==1:					#Se non ce l'ho tra i vicini lo aggiungo
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
			if ricercaPKTID(PKTID,listaPKTIDnear)==1 :										#Controllo se già arrivato, se non: aggiungo a listaPKTIDnear, mando ANEA e ritrasmetto
				listaPKTIDnear[indicePKTIDnear]=IDpacchetti(PKTID,time.time())
				indicePKTIDnear=indicePKTIDnear+1
				print "Pacchetto NEAR ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",TTL
				pacchettoANEA=anea(PKTID,mioIP,PortaQuery)
				v=threadRicerca(IPparametro,Portaparametro,pacchettoANEA,-1)				#Trasmetto ANEA
				v.start() 	
				scriviLog("Invio "+pacchettoANEA+" Vicino "+IPparametro+":"+Portaparametro)		
				if(int(TTL)>1):																#Ritrasmetto NEAR
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)	
					pacchetto=near(PKTID,IPparametro,Portaparametro,TTL)						
					i=0
					while i< len(listaVicini):
						if(listaVicini[i].IP != IPparametro and listaVicini[i].IP !=ip):
							vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i)
							vicini[i].start()	
							scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)													
						i=i+1					
			else:
				scriviLog("!!!!SCARTATO Pacchetto NEAR  "+ self.id+" : "+PKTID+" "+IPparametro+" "+Portaparametro+" "+TTL)

		if identificativo =="QUER":
			ip=creaIP(self.id)
			PKTID=self.socketACK.recv(16)
			PKTID=controlla16B(16,PKTID)
			IPparametro=self.socketACK.recv(39)
			Portaparametro=self.socketACK.recv(5)
			TTL=self.socketACK.recv(2)
			Ricerca1=self.socketACK.recv(20)
			Ricerca=elimina_asterischi(Ricerca1)
			pacchettoR=identificativo+PKTID+IPparametro+Portaparametro+TTL+Ricerca
			if ricercaPKTID(PKTID,listaPKTID)==1 :											#Se PKTID non è presente nella lista, salvo, inoltro, cerco
				print "Pacchetto QUER ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",Ricerca," ",TTL	
				listaPKTID[indicePKTID]=IDpacchetti(PKTID,time.time())
				indicePKTID=indicePKTID+1		
				if(int(TTL)>1):																#Inoltro QUER
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)						
					pacchetto=query(PKTID,IPparametro,Portaparametro,TTL,Ricerca)
					i=0
					while i< len(listaVicini):
						if(listaVicini[i].IP != IPparametro and listaVicini[i].IP != ip):	#Controllo di non rimandarlo al mittente
							vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i)
							vicini[i].start() 	
							scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)							
						i=i+1
			
				fileTrovati=cercaFile(Ricerca)												#Cerco se ho dei risultati nella mia cartella ./immagine	
				if len(fileTrovati) >0:														#Se la ricerca è positiva invio 1 per uno gli AQUE	
					k=0
					while k< len(fileTrovati): 
						socketAQUE=creazioneSocket(IPparametro,Portaparametro)							
						pacchetto=aque(PKTID,mioIP,PortaDownload,fileTrovati[k])	
						socketAQUE.send(pacchetto)											#Invio AQUE	
						k=k+1						
						socketAQUE.close()
						scriviLog("Invio "+pacchetto+" Vicino "+IPparametro+":"+Portaparametro)							
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)			
		self.socketACK.close()
		
	#Funzione per chiudere la socket di ascolto		
	def close(self, nodestroy=False):
		self.log('Disconnetting')
		self.receive=0
		self.socketACK.close()

		if not nodestroy:
			del self.server.gestioneRisposte[self.id]

	def log(self, msg):
		self.server.log('Client '+self.id+': '+msg)					


#Aggiungo un vicino "a mano"
scriviLog("NUOVA SESSIONE") 
Porta=creaPorta(5, "03000")
IP=creaIP("fd00::7ed1:c3ff:fe76:362a") 
listaVicini[0]=Vicini(IP,Porta)
scriviLog("Primo vicino: "+IP+":"+Porta)

#Salvo gli md5 dei file che voglio condividere
SalvaFile()
j=0

#Avvio l'ascolto per possibili download
s=server()
s.start()

#Avvio il thread di ascolto generale
ascolto=ThreadAscolto(PortaQuery)
ascolto.start()
scriviLog("Threads partiti")

#Menù per il cmd
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

		
		if scelta=="1":																#Ricerca di un file
			spegniRicerca=0
			parametri={}
			indiceParametri=0
			TTL=raw_input("Inserisci Time to live (TTL): ")
			TTL=controllaDimensione(TTL)
			Ricerca=raw_input("Inserisci la stringa di ricerca: ")			
			PKTID=generaPKTID(16)
			PKTID=controlla16B(16,PKTID)
			PKTIDmio[j]=IDpacchetti(PKTID,time.time())
			j=j+1
			pacchetto=query(PKTID,mioIP,PortaQuery,TTL,Ricerca)
			i=0			
			while i< len(listaVicini):													#Invio a tutti i vicini mediante threadRicerca		
				vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i)
				vicini[i].start()
				scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)
				i=i+1				
				
		if scelta=="2" : 																#Ricerca vicini
			indiceLista=1
			TTL=raw_input("Inserisci Time to live (TTL) per i vicini: ")
			TTL=controllaDimensione(TTL)
			try:																		#Invio NEAR al vicino di default
				socketVicino1=creazioneSocket(listaVicini[0].IP,listaVicini[0].PORTA)	
				PKTID=generaPKTID(16)
				PKTID=controlla16B(16,PKTID)	
				pacchetto=near(PKTID,mioIP,PortaQuery,TTL)
				socketVicino1.send(pacchetto)	
				socketVicino1.close()
			except:
				print "Il nodo si è disconnesso."
			
		
			
		if scelta=="3": 																#Download file			
			print "download file in corso....."
			loc="./fileScaricati/"
			recvfn	= raw_input("Inserisci il nome del file.estensione per salvare: ")
			if loc[-1] != os.sep: 
				loc += os.sep
			fd = os.open(loc+recvfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0600)			
			indice=raw_input("Inserisci indice del file da scaricare: ")				#Cerco in parametri
			spegniRicerca=1
			IP=parametri[int(indice)].IP
			Porta=parametri[int(indice)].PORTA
			Filemd5=parametri[int(indice)].FILEMD5		
			socketD=download(IP,Porta,Filemd5)

			risposta=socketD.recv(10) 													#Ricevo ARET+nChunk
			if not risposta:
				print "ERRORE RICEZIONE PACCHETTO DOWNLOAD DAL PEER"
				sys.exit(1)
			identificativo=risposta[0:4]
			if identificativo !="ARET":
				print "ERRORE RISPOSTA DOWNLOAD PEER"
			nChunk=int(risposta[4:10])  			
			conta=1	
			while conta <= nChunk:														#Ciclo per leggere i chunk e ricevere il file
				lenChunk=socketD.recv(5)
				while len(lenChunk)<5:													#Se <5 avanzo 1 byte alla volta
					lenChunk=lenChunk+socketD.recv(1)
				lenChunk=int(lenChunk)	
				
				data=socketD.recv(lenChunk)												#Ricevo chunk
				while len(data)<lenChunk:
					data=data+socketD.recv(1)
				os.write(fd, data)	
				conta=conta+1			
			print "Il file è stato salvato con successo!"			
			os.close(fd)			
			socketD.close() 
			
		if scelta=="4":																	#Stampo la lista dei vicini
			stampaVicini(listaVicini)
			
		if scelta=="5":																	#Stampo la lista dei PKTID
			stampa(listaPKTID)
		
		if scelta=="6":																	#Chiudo le socket aperte (download e ascolto)
			s.closeMain()
			ascolto.closeSocketACK()
			print "...FINE...."
			break
			
