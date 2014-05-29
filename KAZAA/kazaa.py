#KAZAA GRUPPO 03
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


mioIP="fd00:0000:0000:0000:22c9:d0ff:fe47:70a3"
PortaQuery="03000"
gestioneRisposte={}
gestioneRisposte20s={}
listaVicini={} 									#Lista degli ip e porta dei vicini
vicini={} 										#Thread per fare query ai vicini
parametri={}									#Lista parametri per il download
indiceListaSuperPeer=0
listaSuperPeer={} 								#Lista dei super peer ricevuti dal pacchetto ASUP
fileCondivisi={}								#Lista file condivisi
fileTrovati={}									#Lista file trovati
spegniRicerca=0
superPeer=0 									#0=peer,1=superpeer									
listaPKTID={}  									#Lista dei PKTID dei QUER che mi arrivano e ritrasmetto
listaPKTIDquer={}
listaPKTIDsupe={} 								#Lista che salva i PKTID di tutti i pacchetti SUPE ricevuti
listaPKTIDquerFind={} 							#Lista dei PKTID dei pacchetti QUER il superpeer trasmette dopo una FIND
listaPKTIDasup={}								#Lista dei pktid delle risposte asup
sessionidPKTID={}								#Lista che ha come indice il sessionId e ad ognuno è associato il pktid del pachetto QUER che genera il superpeer quando arriva una FIND
salvataggio={} 									#Lista dei parametri di AFIN
indice=0 										#Indice di "salvataggio" per il pacchetto AFIN
listaLoggati={} 								#Lista dei peer che si sono loggati da noi
listaFile=[]									#Lista della tabella ADFF--> istanza della classe StrutturaFile
listaRispAque=[]								#Lista che contiene le risposte Aque
ricercheSuperPeer=[] 

class creaLISTAIPPORTA:
	def __init__(self, IP, PORTA):
		self.IP=IP
		self.PORTA=PORTA


class creaLISTA:
	def __init__(self, FILEMD5, FILENAME, IP, PORTA):
		self.FILEMD5=FILEMD5
		self.FILENAME=FILENAME
		self.LISTAIPPORTA=[]
		l=creaLISTAIPPORTA(IP, PORTA)
		self.LISTAIPPORTA.append(l)


class  creaListaRispAque:
	def __init__(self, PKTID, FILEMD5, FILENAME, IP, PORTA):
		self.PKTID=PKTID
		self.LISTA=[]
		l=creaLISTA(FILEMD5, FILENAME, IP, PORTA)
		self.LISTA.append(l)

class StrutturaFile:
	def __init__(self,FILEMD5,FILENAME,SESSIONID):	
		self.SESSIONID=[]
		self.FILENAME=FILENAME
		self.FILEMD5=FILEMD5
		self.SESSIONID.append(SESSIONID)

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
	PKTID=''
	def __init__(self,IP, PORTA, FILEMD5,FILENAME,PKTID):		
		self.IP=IP
		self.PORTA=PORTA
		self.FILEMD5=FILEMD5
		self.FILENAME=FILENAME
		self.PKTID=PKTID

#Classe per salvare sessionId,ip e porta dei peer quando si loggano a noi (siamo superpeer)	
class Loggati:

	IP=''
	PORTA=''
	def __init__(self,IP, PORTA):
		self.IP=IP
		self.PORTA=PORTA

#Funzione per leggere dato da socket
def leggi(s,dim):
	dato=s.recv(dim)
	while len(dato)<dim:
		dato=dato+s.recv(1)
	return dato

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
	
	
#Funzione per la stampa di una lista
def stampa(l): 
	for elemento in l.keys():
		print elemento,l[elemento]

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
def cancellaPacchettiScaduti(lista,tempo,Tmax):
	for i in lista.keys():
			if tempo-lista[i] >= Tmax:							#differenza tra tempo attuale e stamp di quando ho ricevuto il pacchetto
				del lista[i]		
	
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

#Funzione per il controllo dato IP e porta si un peer se è un vicino (0 se vicino,1 se non vicino)
def ricercaVicini(IP,Porta,lista):
	i=0
	while i < len(lista):
		if lista[i].IP==IP and lista[i].PORTA==Porta:
			return 0
		i=i+1
	return 1		
	
#Controllo la dimensione di un numero e la riempo di 0 fino a dim
def controllaArgomentoNumero(dim,argomento):
	if len(argomento) < dim :
		differenza=dim-len(argomento)
		i=0
		while i<differenza:
			argomento="0"+argomento
			i=i+1
	return argomento

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

#Funzione per il controllo se un file esiste
def esisteFile(percorsoFile):
	try:
		fd=open(percorsoFile,"rb")		
		return 1
	except:
		print "Il file non esiste"
		return 0

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

#Funzione per la creazione del pacchetto SUPE
def supe(PKTID,IP,PortaQuery,TTL):	
	pacchetto="SUPE"+PKTID+IP+PortaQuery+TTL
	return pacchetto

#Funzione per la creazione del pacchetto ASUP
def asup(PKTID,IP,PortaQuery):	
	pacchetto="ASUP"+PKTID+IP+PortaQuery
	return pacchetto

#Funzione per la creazione del pacchetto AQUE
def aque(PKTID,IP,P,Filemd5,Filename):	
	pacchetto="AQUE"+PKTID+IP+P+Filemd5+Filename	
	return pacchetto

#Funzione per la richiesta di download RETR con creazione della socket peer-peer e invio 	
def download(IPP2P,PortaP2P,Filemd5):
	socketD=creazioneSocket(IPP2P,PortaP2P)	
	Filemd5=controlla16B(16,Filemd5)
	pacchetto="RETR"+Filemd5
	socketD.send(pacchetto)
	return 	socketD

#Funzione per la creazione del pacchetto LOGI
def logi(peer_socket,IP,PORTA):
	pacchetto="LOGI"+IP+PORTA
	peer_socket.send(pacchetto)
	return peer_socket	
	
#Funzione per la creazione del pacchetto ALGI
def algi(peer_socket,SessionID):
	SessionID=controlla16B(16,SessionID)
	pacchetto="ALGI"+SessionID
	peer_socket.send(pacchetto)

#Funzione per la creazione del pacchetto LOGO
def logo(peer_socket,SessionID):
	SessionID=controlla16B(16,SessionID)
	pacchetto="LOGO"+SessionID
	peer_socket.send(pacchetto)

#Funzione per la creazione del pacchetto ALGO
def algo(peer_socket,n):
	pacchetto="ALGO"+n
	peer_socket.send(pacchetto)

#Funzione per la creazione del pacchetto ADFF
def adff(peer_socket,SessionID,Filemd5,Filename): #aggiunta file
	Filemd5=controlla16B(16,Filemd5)
	Filename=controllaArgomentoStringa(100,Filename)
	SessionID=controlla16B(16,SessionID)
	pacchetto="ADFF"+SessionID+Filemd5+Filename
	peer_socket.send(pacchetto)

#Funzione per la creazione del pacchetto DEFF
def deff(peer_socket,SessionID,Filemd5): #rimozione file
	Filemd5=controlla16B(16,Filemd5)
	SessionID=controlla16B(16,SessionID)
	pacchetto="DEFF"+SessionID+Filemd5
	peer_socket.send(pacchetto)

#Funzione per la creazione del pacchetto FIND
def find(peer_socket,SessionID,Ricerca): #ricerca rivolta dal peer al super peer
	SessionID=controlla16B(16,SessionID)
	Ricerca=controllaArgomentoStringa(20,Ricerca)
	pacchetto="FIND"+SessionID+Ricerca
	peer_socket.send(pacchetto)

#Funzione per la creazione del pacchetto RETR
def retr(IPP2P,PortaP2P,Filemd5):	
	peer_socketPeer = creazioneSocket(IPP2P,PortaP2P)
	Filemd5=controlla16B(16,Filemd5)
	pacchetto="RETR"+Filemd5
	peer_socketPeer.send(pacchetto)
	return 	peer_socketPeer

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
	acceso=1
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

		self.socketACK.settimeout(1000)
		while self.acceso:
			try:				
				(conn, addr) = self.socketACK.accept()
				cid=addr[0]								
				gestioneRisposte[cid]=threadRisposte(cid, conn,self)					#Delego a threadRisposte
				gestioneRisposte[cid].start()
			except socket.timeout:
				print "Tempo scaduto.....cancellazione pacchetti in corso.."	
				tempo=time.time()														#Salvo time stamp per controllare quali eliminare
				cancellaPacchettiScaduti(listaPKTID,tempo,5000) 						#Lista pktid:pktid dei quer che ritrasmetto
				cancellaPacchettiScaduti(listaPKTIDsupe,tempo,5000)						#Lista pktidsupe:pktid dei supe che ritrasmetto
				self.socketACK.settimeout(1000)

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
				
		global listaPKTID
		global listaPKTIDsupe
		global listaVicini
		global spegniRicerca
		global listaPKTIDasup		
		global listaSuperPeer
		global indiceListaSuperPeer
		global sessionidPKTID
		global listaLoggati
		global listaFile
		global listaPKTIDquerFind
		global listaPKTIDquer
		global superPeer
		global fileCondivisi

		identificativo=leggi(self.socketACK,4)											#Ricezione dell'identificativo del pacchetto
		
		if not identificativo:
			print "ERRORE RICEZIONE identificativo threadRisposte"
			sys.exit(1)					
		if identificativo !="RETR" and identificativo !="ASUP" and identificativo !="SUPE" and identificativo !="QUER" and identificativo !="FIND" and identificativo !="LOGI" and identificativo !="ADFF" and identificativo !="DEFF" and identificativo !="LOGO":
			print "ERRORE RISPOSTA IDENTIFICATIVO ASUP, SUPE,QUER,FIND..."
			self.socketACK.close()	
				
		if identificativo =="RETR":					
			Filemd5=leggi(self.socketACK,16)	
			Filemd5=controlla16B(16,Filemd5)		
			percorsoFile=trovaPercorso(fileCondivisi,Filemd5)							#Trovo il file e lo divido in chunk da 4096
			fd = os.open(percorsoFile,os.O_RDONLY)		
			filesize = os.fstat(fd)[stat.ST_SIZE]		
			nChunk=filesize/4096    
			
			if (filesize%4096) !=0:  													#Se dividibile per 4096 invio, altrimenti aggiungo un chunk
				nChunk=nChunk+1	
			nChunk=str(nChunk).zfill(6)													#Fill con 0 del numero dei chunk fino a 6
					
			pacchetto="ARET"+nChunk
			print "Trasferimento in corso.."
			i=1
			while i<= int(nChunk):														#Ciclo per la costruzione dell'ARET
				buf=os.read(fd,4096)				
				if not buf: 
					break
				lBuf=len(buf)
				lBuf=str(lBuf).zfill(5)	
				pacchetto=pacchetto+lBuf+buf
				i=i+1	
			print "Trasferimento effettuato!!"			
			self.socketACK.send(pacchetto) 												#Invio dell'ARET
			os.close(fd)
			time.sleep(50)		
			self.socketACK.close()	
		
		if identificativo =="ASUP":
			ip=creaIP(self.id)
			PKTID=leggi(self.socketACK,16)
			PKTID=controlla16B(16,PKTID)
			IPparametro=leggi(self.socketACK,39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=leggi(self.socketACK,5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			pacchettoR=PKTID+IPparametro+Portaparametro						
			if superPeer==0: 															#Se sono un peer controllo se gia nella lista e eventualmente aggiungo 
				if listaPKTIDasup.has_key(PKTID)==0: 									#Se pktid non è presente nella lista aggiungo
					print "Pacchetto ASUP ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro
					scriviLog("Ricevuto ASUP dal peer "+ self.id+" : "+PKTID+" "+IPparametro+" "+Portaparametro)
					listaPKTIDasup[PKTID]=time.time()					
					listaSuperPeer[indiceListaSuperPeer]=Vicini(IPparametro,Portaparametro)	
					scriviLog("Super Peer aggiunto: "+IPparametro+" "+Portaparametro)				
				else:
					scriviLog("!!Pacchetto Scartato!!!! ASUP"+pacchettoR+" ricevuto del peer"+ip)
			
			if superPeer==1: 															#Se sono un super peer, aggiungo alla listaSuperPeer se non c'è gia
				if ricercaVicini(IPparametro,Portaparametro,listaSuperPeer) ==1: 		#Se super non è presente nella listaSuperPeer aggiungo			
					listaSuperPeer[indiceListaSuperPeer]=Vicini(IPparametro,Portaparametro)
					indiceListaSuperPeer=indiceListaSuperPeer+1
					print "Pacchetto ASUP ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro
				
				else:
					scriviLog("!!Pacchetto Scartato!!!! "+pacchettoR+" ricevuto del peer"+ip)	
			
		if identificativo =="SUPE":
			ip=creaIP(self.id)
			PKTID=leggi(self.socketACK,16)
			PKTID=controlla16B(16,PKTID)
			IPparametro=leggi(self.socketACK,39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=leggi(self.socketACK,5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			TTL=leggi(self.socketACK,2)
			TTL=controllaDimensione(TTL)
			pacchettoR=identificativo+PKTID+IPparametro+Portaparametro
			if listaPKTIDsupe.has_key(PKTID) == 0 : 									#Controllo se già arrivato, se non: aggiungo a listaPKTIDsupe, mando ASUP se sono super e ritrasmetto 
				listaPKTIDsupe[PKTID]=time.time()										
				print "Pacchetto SUPE ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",TTL
				scriviLog("Ricevuto SUPE da "+self.id+" : "+IPparametro+":"+Portaparametro+" TTL:"+TTL)
				if superPeer==1: 														#Se sono un super peer rispondo con ASUP					
					if IPparametro!=mioIP:
						pacchetto=asup(PKTID,mioIP,PortaQuery)
						v=threadRicerca(IPparametro,Portaparametro,pacchetto,-1)
						v.start()
						scriviLog("Invio "+pacchetto+" Vicino "+IPparametro+":"+Portaparametro)	
				if(int(TTL)>1):  														#Ritrasmetto SUPE
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)	
					pacchetto=supe(PKTID,IPparametro,Portaparametro,TTL)						
					i=0
					while i< len(listaVicini):
						if(listaVicini[i].IP != IPparametro and listaVicini[i].IP !=ip):
							vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i)
							vicini[i].start()	
							scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)													
						i=i+1	
				
			else:
				scriviLog("!!Pacchetto Scartato!!!! "+pacchettoR+" ricevuto del peer"+ip)
					
		if identificativo =="QUER":
			ip=creaIP(self.id)
			PKTID=leggi(self.socketACK,16)
			PKTID=controlla16B(16,PKTID)
			IPparametro=leggi(self.socketACK,39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=leggi(self.socketACK,5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			TTL=leggi(self.socketACK,2)
			TTL=controllaDimensione(TTL)
			Ricerca1=leggi(self.socketACK,20)
			Ricerca=elimina_asterischi(Ricerca1)
			Ricerca=controllaArgomentoStringa(20,Ricerca)	
			Ricerca=Ricerca.strip()
			pacchettoR=identificativo+PKTID+IPparametro+Portaparametro+TTL+Ricerca
			if listaPKTID.has_key(PKTID)==0: 													#Se PKTID non è presente nella lista, salvo, inoltro, cerco
				print "Pacchetto QUER ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",Ricerca," ",TTL	
				scriviLog("Pacchetto QUER ricevuto dal peer "+ self.id+" : "+PKTID+" "+IPparametro+" "+Portaparametro+" "+Ricerca+" "+TTL)	
				listaPKTID[PKTID]=time.time()				
				if(int(TTL)>1):																	#Inoltro QUER
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)						
					pacchetto=query(PKTID,IPparametro,Portaparametro,TTL,Ricerca)
					i=0
					while i< len(listaSuperPeer):
						if(listaSuperPeer[i].IP != IPparametro and listaSuperPeer[i].IP != ip): #Controllo di non rimandarlo al super peer mittente
							vicini[i]=threadRicerca(listaSuperPeer[i].IP,listaSuperPeer[i].PORTA,pacchetto,i)
							vicini[i].start() 	
							scriviLog("Invio "+pacchetto+" Vicino "+listaSuperPeer[i].IP+":"+listaSuperPeer[i].PORTA)							
						i=i+1
			
				p=re.compile(Ricerca,re.IGNORECASE)												#Cerco se ho dei risultati nei miei file e invio AQUE
				for i in listaFile:
					if p.search(i.FILENAME):													#Se ho trovato il file invio AQUE
						for l in i.SESSIONID:
							FILENAME=controllaArgomentoStringa(100,i.FILENAME)
							pacchetto=aque(PKTID,listaLoggati[l].IP,listaLoggati[l].PORTA,i.FILEMD5,FILENAME)
							socketAQUE=creazioneSocket(IPparametro,Portaparametro)
							socketAQUE.send(pacchetto)	
							socketAQUE.close()
							scriviLog("Invio "+pacchetto+" Vicino "+IPparametro+":"+Portaparametro)							
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)		

		if identificativo =="FIND":							
			ip=creaIP(self.id)
			SessionID=leggi(self.socketACK,16)
			SessionID=controlla16B(16,SessionID)
			Ricerca=leggi(self.socketACK,20)
			Ricerca=controllaArgomentoStringa(20,Ricerca)
			Ricerca=Ricerca.strip()
			pacchettoR=identificativo+SessionID+Ricerca
			print "Arrivato ",pacchettoR, "dal peer: ", ip
			scriviLog("Arrivato "+pacchettoR+ "dal peer: "+ ip)
			if superPeer==1: 																	#Se sono superpeer cerco file, invio QUER
				PKTID=generaPKTID(16)
				sessionidPKTID[PKTID]=SessionID
				TTL="03"
				TTL=controllaDimensione(TTL)
				PortaAscolto20s=randint(40000,60000)											#Scelgo porta random
				pacchettoQUER=query(PKTID,mioIP,str(PortaAscolto20s),TTL,Ricerca)				
				listaPKTIDquerFind[PKTID]=time.time()											#Salvo pacchetto nella lista della FIND per controllo tempo
				
				p=re.compile(Ricerca,re.IGNORECASE)												#Preparo la ricerca
				for i in listaFile:
					if p.search(i.FILENAME):													#Se ho trovato il file nella listaFile per nome
						if listaPKTIDquerFind.has_key(PKTID) == 1: 								#Se è presente nella lista delle FIND
							trovatoPKTID=0
							for indice in listaRispAque:										#Se lo trovo nella lista delle risp AQUE esco dal ciclo										
								if indice.PKTID==PKTID:
									trovatoPKTID=1
									break
							if trovatoPKTID==1:													#Se già nella lista risposte AQUE
								trovatoMD5=0
								for chiave in indice.LISTA:
									if chiave.FILEMD5==i.FILEMD5:
										trovatoMD5=1
										break	
								if trovatoMD5==1:												#Se anche l'md5 coincide, salvo ip e porta di chi ce l'ha
									for s in range(len(i.SESSIONID)):							
										if SessionID != i.SESSIONID[s]:
											chiave.LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
								else:
									if SessionID != i.SESSIONID[0]:								#Aggiungo peer ai possessori
										indice.LISTA.append(creaLISTA(i.FILEMD5,i.FILENAME, listaLoggati[i.SESSIONID[0]].IP,listaLoggati[i.SESSIONID[0]].PORTA))
										for s in range(1,len(i.SESSIONID)):
											if SessionID != i.SESSIONID[s]:
												indice.LISTA[len(indice.LISTA)-1].LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
									else:
										if len(i.SESSIONID)!=1:
											indice.LISTA.append(creaLISTA(i.FILEMD5,i.FILENAME, listaLoggati[i.SESSIONID[1]].IP,listaLoggati[i.SESSIONID[1]].PORTA))
											for s in range(2,len(i.SESSIONID)):
												if SessionID != i.SESSIONID[s]:
													indice.LISTA[len(indice.LISTA)-1].LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
									
							else:																#Se il pktid non è ancora presente aggiungo nella lista AQUE
								if SessionID != i.SESSIONID[0]:
									listaRispAque.append(creaListaRispAque(PKTID,i.FILEMD5,i.FILENAME, listaLoggati[i.SESSIONID[0]].IP,listaLoggati[i.SESSIONID[0]].PORTA))															
									for s in range(1,len(i.SESSIONID)):
										if SessionID != i.SESSIONID[s]:
											listaRispAque[len(listaRispAque)-1].LISTA[0].LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
								else:
									if len(i.SESSIONID)!=1:
										listaRispAque.append(creaListaRispAque(PKTID,i.FILEMD5,i.FILENAME, listaLoggati[i.SESSIONID[1]].IP,listaLoggati[i.SESSIONID[1]].PORTA))															
										for s in range(2,len(i.SESSIONID)):
											if SessionID != i.SESSIONID[s]:
												listaRispAque[len(listaRispAque)-1].LISTA[0].LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
				
				s=ThreadAscolto20s(PortaAscolto20s)												#Avvio il thread che aspetta le AQUE
				s.start()
												
				
				k=0
				while k< len(listaSuperPeer): 													#Invio la QUER ai superpeer
						socketFIND=creazioneSocket(listaSuperPeer[k].IP,listaSuperPeer[k].PORTA)												
						socketFIND.send(pacchettoQUER)	
						k=k+1						
						socketFIND.close()
						scriviLog("Invio "+pacchettoQUER+" Vicino "+listaSuperPeer[k-1].IP+":"+listaSuperPeer[k-1].PORTA)	
				s.join(20)
				s.closeSocketAscolto20s()
				s.stop()
				print "Sono scaduti i 20sec"					
							
				for i in listaRispAque: 														#Scorro i PKTID						
					if PKTID==i.PKTID:	
						numMD5="%03d" % len(i.LISTA)
						pacchetto="AFIN"+ numMD5
						pacchettoPrint="AFIN "+ numMD5+"\n"
						for k in i.LISTA: 														#Scorro gli MD5
							FILENAME=controllaArgomentoStringa(100,k.FILENAME)
							numIPPORTA="%03d" % len(k.LISTAIPPORTA)
							pacchetto= pacchetto+k.FILEMD5+FILENAME+numIPPORTA
							pacchettoPrint=pacchettoPrint+" "+FILENAME.strip()+" "+numIPPORTA
							for ipp in k.LISTAIPPORTA: 											#Scorro gli IP e le PORTE
								pacchetto= pacchetto+ipp.IP+ipp.PORTA
								pacchettoPrint=pacchettoPrint+" ip:"+ipp.IP+" porta:"+ipp.PORTA+"\n"
						scriviLog("Inviato "+pacchetto)
						print pacchettoPrint
				print pacchetto					
				self.socketACK.send(pacchetto)				
				
				listaPKTIDquerFind={} 															#Azzero la lista listaPKTIDquerFind				
				print
				print				
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)		
				
		if identificativo =="LOGI":	
			ip=creaIP(self.id)
			IPparametro=leggi(self.socketACK,39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=leggi(self.socketACK,5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			pacchettoR=identificativo+IPparametro+Portaparametro
			print "Ricevuto LOGI da "+IPparametro+":"+Portaparametro
			scriviLog("Ricevuto LOGI da "+IPparametro+":"+Portaparametro)	
			if superPeer==1: 																	#Se sono super peer
																								#Controllo che ip e porta non siano gia presenti nella listaLoggati
				peerPresente=0 																	#Il peer non si era ancora loggato
				for chiave in listaLoggati.keys():
					if IPparametro==listaLoggati[chiave].IP and Portaparametro==listaLoggati[chiave].PORTA:
						peerPresente=1 															#Peer gia loggato
						SessionID="0000000000000000"
						scriviLog("Peer già loggato")	
						break
				if peerPresente==0:	
					SessionID=generaPKTID(16) 													#Genero il sessionID
					listaLoggati[SessionID]=Loggati(IPparametro,Portaparametro)
					
				pacchettoALGI="ALGI"+SessionID
				algi(self.socketACK,SessionID)
				scriviLog("Inviato "+pacchettoALGI+ " a "+IPparametro+" : "+Portaparametro)	
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)	
			
		if identificativo =="ADFF":	
			ip=creaIP(self.id)
			SessionID=leggi(self.socketACK,16)
			SessionID=controlla16B(16,SessionID)
			Filemd5=leggi(self.socketACK,16)
			Filemd5=controllaArgomentoStringa(16,Filemd5)
			Filename=leggi(self.socketACK,100)
			Filename=controllaArgomentoStringa(100,Filename)
			Filename=Filename.strip()
			pacchettoR=identificativo+SessionID+Filemd5+Filename
			print "Ricevuto pacchetto "+pacchettoR+" da utente "+ip
			if superPeer==1: 																	#Se sono super peer				
				if listaLoggati.has_key(SessionID): 											#Controllo che il SessionID sia loggato (Se la chiave SessionID è presente)		
					filePresente=0
					for files in listaFile:														#Controllo che non sia già presente il filemd5
						if files.FILEMD5==Filemd5: 												#Se il filemd5 è presente allora lo rinomino
							filePresente=1
							files.FILENAME=Filename
							trovato=0
							for id in range(len(files.SESSIONID)): 								#Controllo che il SessionID che ha aggiunto il file è gia presente
								if files.SESSIONID[id]==SessionID:	
									trovato=1
									break 
							if trovato==0: 														#SessionId non presente	
								files.SESSIONID.append(SessionID) 								#Aggiungo il SessionID per il filemd5 inserito
					if filePresente==0: 														#Il filemd5 non è presente nella tabella
						riga=StrutturaFile(Filemd5,Filename,SessionID)
						listaFile.append(riga)							
				else:
					print "Ricevuto pacchetto "+pacchettoR+" da utente "+ip+" NON LOGGATO"					
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)			
				
		if identificativo =="DEFF":	
			ip=creaIP(self.id)
			SessionID=leggi(self.socketACK,16)
			SessionID=controlla16B(16,SessionID)
			Filemd5=leggi(self.socketACK,16)
			Filemd5=controllaArgomentoStringa(16,Filemd5)				
			pacchettoR=identificativo+SessionID+Filemd5
			if superPeer==1: 																	#Se sono super peer	
				if listaLoggati.has_key(SessionID): 											#Controllo che il SessionID sia loggato (Se la chiave SessionID è presente)	
					print "Ricevuto pacchetto "+pacchettoR+" da utente "+ip
					for file in listaFile:
						if file.FILEMD5==Filemd5:
							file.SESSIONID.remove(SessionID) 									#Cancello il SessionID-->quel SessionID non è più associato a quel filemd5
							if len(file.SESSIONID)==0: 
								listaFile.remove(file)						
				else:
					print "Ricevuto pacchetto "+pacchettoR+" da utente "+ip+" NON LOGGATO"	
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)	
				
		if identificativo =="LOGO":	
			ip=creaIP(self.id)
			SessionID=leggi(self.socketACK,16)
			SessionID=controlla16B(16,SessionID)				
			pacchettoR=identificativo+SessionID
			if superPeer==1: 																	#Se sono super peer	
				if listaLoggati.has_key(SessionID): 											#Controllo che il SessionID sia loggato (Se la chiave SessionID è presente)	
					nCancellati=0
														
					for file in listaFile:
						for i in range(len(file.SESSIONID)):
							if file.SESSIONID[i]==SessionID:
								file.SESSIONID.pop(i) 
								nCancellati=nCancellati+1
					for file in range(len(listaFile),0):
						if len(listaFile[file].SESSIONID) == 0:
							listaFile.pop(file)
					
					nCancellati=controllaArgomentoNumero(3,str(nCancellati))
					algo(self.socketACK,nCancellati)
					listaLoggati.pop(SessionID)
					pacchettoALGO="ALGO"+nCancellati
					scriviLog("Inviato "+pacchettoALGO+ " a "+ip)	
					print "Ricevuto pacchetto "+pacchettoR+" da utente "+ip
				else:
					print "Ricevuto pacchetto "+pacchettoR+" da utente "+ip+" NON LOGGATO"	
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)	
								
		self.socketACK.close()		
					
	def close(self, nodestroy=False):
		self.log('Disconnetting')
		self.receive=0
		self.socketACK.close()

		if not nodestroy:
			del self.server.gestioneRisposte[self.id]

	def log(self, msg):
		self.server.log('Client '+self.id+': '+msg)

#Thread per la query da 20s riguardo le query di ricerca 
class ThreadAscolto20s(threading.Thread):
	ip=""
	porta=""		
	socketAscolto20s=''
	acceso=1
	def __init__(self,Porta):
		threading.Thread.__init__(self)		
		self.porta=Porta
				
	def run(self):
		global listaPKTIDquer
		global listaPKTIDquerFind
		global listaLoggati
		global listaRispAque
		global ricercheSuperPeer
		global superPeer

		
		self.socketAscolto20s=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		self.socketAscolto20s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socketAscolto20s.bind(("", int(self.porta)))
		self.socketAscolto20s.listen(5)
			
	
		while self.acceso:							
			(conn,addr) = self.socketAscolto20s.accept()
			cid=addr[0]
			gestioneRisposte20s[cid]=threadRisposte20s(cid, conn,self)
			gestioneRisposte20s[cid].start()
				
	def log(self, msg):
		print(msg)

	def closeSocketAscolto20s(self):
		self.socketAscolto20s.close()
		return True

	def stop(self):
		self.acceso=0
			
		
#Thread per le risposte AQUE				
class threadRisposte20s(threading.Thread): 
	id=''
	socketRisposte20s=None	
	receive=1
	server=None
	def __init__(self, id, socket, server):
		threading.Thread.__init__(self)
		self.id=id
		self.socketRisposte20s=socket
		self.server=server		
		
	def run(self):	
					
		global listaPKTID
		global listaPKTIDsupe
		global listaVicini
		global spegniRicerca		
		global listaSuperPeer
		global indiceListaSuperPeer
		global salvataggio																	#Lista parametri AFIN
		global indice 
		global listaRispAque

		identificativo=leggi(self.socketRisposte20s,4)
		
		if not identificativo:
			print "ERRORE RICEZIONE PACCHETTO 20S"
			sys.exit(1)					
		if identificativo !="AQUE":
			print "ERRORE RISPOSTA IDENTIFICATIVO AQUE"

		if identificativo =="AQUE":			
			self.id=creaIP(self.id)
			PKTID=leggi(self.socketRisposte20s,16)
			PKTID=controlla16B(16,PKTID)
			IPparametro=leggi(self.socketRisposte20s,39)
			IPparametro=controllaArgomentoStringa(39,IPparametro)
			Portaparametro=leggi(self.socketRisposte20s,5)
			Portaparametro=controllaArgomentoStringa(5,Portaparametro)
			Filemd5=leggi(self.socketRisposte20s,16)
			Filemd5=controlla16B(16,Filemd5)
			Filename=leggi(self.socketRisposte20s,100)
			Filename=Filename.strip();
			
			if listaPKTIDquerFind.has_key(PKTID) == 1 or listaPKTIDquer.has_key(PKTID) == 1: #Se è presente il pktid, corrisponde ad una richiesta
				trovatoPKTID=0
				for indice in listaRispAque:
					if indice.PKTID==PKTID:
						trovatoPKTID=1
						break
						
				if trovatoPKTID==1:
					trovatoMD5=0
					for chiave in indice.LISTA:
						if chiave.FILEMD5==Filemd5:
							trovatoMD5=1
							break	
							
					if trovatoMD5==1:
						for s in range(len(chiave.LISTAIPPORTA)):
							if chiave.LISTAIPPORTA!=IPparametro:
								chiave.LISTAIPPORTA.append(creaLISTAIPPORTA(IPparametro,Portaparametro))
					else:
						indice.LISTA.append(creaLISTA(Filemd5,Filename, IPparametro,Portaparametro))
						
				else:
					listaRispAque.append(creaListaRispAque(PKTID,Filemd5,Filename, IPparametro,Portaparametro))															
					
				
			else:
				print "Il pacchetto AQUE ricevuto non corrisponde a una nostra richiesta."
									
	def close(self, nodestroy=False):
		self.log('Disconnetting')
		self.receive=0
		self.socketRisposte20s.close()

		if not nodestroy:
			del self.server.gestioneRisposte20s[self.id]

	def log(self, msg):
		self.server.log('Client '+self.id+': '+msg)					

#
print "PROGETTO 3... Scegli cosa vuoi essere:"
print "1. SUPER peer,"
print "2. peer,"
scelta=raw_input("Numero scelta: \n")

if scelta=="1": 																					#SUPER PEER
	superPeer=1
	print "Salve super peer...\n"
	scriviLog("NUOVA SESSIONE super PEER")
	IP=raw_input("Inserisci IP Super peer vicino: ") 
	Porta=raw_input("Inserisci Porta Super peer vicino: ") 
	IP=creaIP(IP) 
	Porta=controllaArgomentoNumero(5,Porta)
	listaVicini[0]=Vicini(IP,Porta)
	scriviLog("Primo vicino: "+IP+":"+Porta)

	SalvaFile() 																					#Salvo i filemd5 e filename che voglio condividere
	lista=(os.listdir('./immagine')	)
	i=0
	while i <len(lista):
		percorso="./immagine/"+lista[i]
		filemd5=creazioneFilemd5(percorso)
		listaFile.append(StrutturaFile(filemd5,lista[i],"00000000000000ME"))
		i=i+1
	
	listaLoggati["00000000000000ME"]=Loggati(mioIP,PortaQuery)
	
	j=0

	ascolto=ThreadAscolto(PortaQuery)																#Avvio il thread di ascolto generale  
	ascolto.start()
	scriviLog("Threads partiti")
	#menu:
	while 1:
			print
			print
			print "OPERAZIONI POSSIBILI:"		
			print "1. ricerca file;"
			print "2. ricerca super peer;"
			print "3. download file;"
			print "4. stampa super peer vicini;"
			print "5. stampa peer collegati;"
			print "6. stampa tutti i file caricati"
			print "7. esci."
			
			
			scelta=raw_input("Numero operazione: \n")

			
			if scelta=="1": 																		#Ricerca file
				spegniRicerca=0
				ricercheSuperPeer=[]						
				TTL=raw_input("Inserisci Time to live (TTL): ")
				TTL=controllaDimensione(TTL)
				Ricerca=raw_input("Inserisci la stringa di ricerca: ")			
				PKTID=generaPKTID(16)
				PKTID=controlla16B(16,PKTID)
				listaPKTIDquer[PKTID]=time.time()  													#Salviamo il PKTID che mandiamo
				j=j+1
				PortaAscolto20s=randint(40000,60000)
				pacchetto=query(PKTID,mioIP,str(PortaAscolto20s),TTL,Ricerca) 						#Costruisco il pacchetto QUER
				s=ThreadAscolto20s(PortaAscolto20s)
				s.start()
				i=0			
				while i< len(listaSuperPeer):														#Invio il pacchetto QUER a tutti i vicini			
					vicini[i]=threadRicerca(listaSuperPeer[i].IP,listaSuperPeer[i].PORTA,pacchetto,i)
					vicini[i].start()
					scriviLog("Invio "+pacchetto+"  Al superpeer "+listaSuperPeer[i].IP+":"+listaSuperPeer[i].PORTA)
					i=i+1	
				s.join(20)
				s.stop()
			
				
				
				p=re.compile(Ricerca.strip(),re.IGNORECASE)											#Inizializzo la ricerca
				for i in listaFile:
					if p.search(i.FILENAME):	 													#Se ci sono risultati
						for l in i.SESSIONID:
							if l!="00000000000000ME":
								ricercheSuperPeer.append(SalvaParametri(listaLoggati[l].IP,listaLoggati[l].PORTA,i.FILEMD5,i.FILENAME,PKTID))
																									#Stampo a video da listaPKTIDquer che sono i risultati del super peer
				for j in listaPKTIDquer.keys(): 
					for i in listaRispAque: 														#Scorro i PKTID
						if j==i.PKTID:				
							for k in i.LISTA: 														#Scorro gli MD5
								for ipp in k.LISTAIPPORTA: 											#Scorro gli IP e le PORTE
									ricercheSuperPeer.append(SalvaParametri(ipp.IP,ipp.PORTA,k.FILEMD5,k.FILENAME,i.PKTID))
				j=0
				for i in ricercheSuperPeer:
					print j,") ",i.FILENAME," ",i.IP," ",i.PORTA
					j=j+1
				listaPKTIDquer={}																	#Azzero la lista listaPKTIDquer	
				
			if scelta=="2" :																		#Ricerca superpeer		
				listaSuperPeer={}
				TTL=raw_input("Inserisci Time to live (TTL) per i vicini: ")
				TTL=controllaDimensione(TTL)
				PKTID=generaPKTID(16)
				PKTID=controlla16B(16,PKTID)	
				pacchetto=supe(PKTID,mioIP,PortaQuery,TTL) 											#Creazione pacchetto NEAR
				try:
					socketVicino1=creazioneSocket(listaVicini[0].IP,listaVicini[0].PORTA)							
					socketVicino1.send(pacchetto)
					socketVicino1.close()
				except:
					print "Il nodo 1 si è disconnesso."	
				try:	
					socketVicino2=creazioneSocket(listaVicini[1].IP,listaVicini[1].PORTA)
					socketVicino2.send(pacchetto)	
					
					socketVicino2.close()
				except:
					print "Il nodo 2 si è disconnesso."					
				
			if scelta=="3": 																		#Download file			
				print "download file in corso....."
				loc="./fileScaricati/"
				recvfn	= raw_input("Inserisci il nome del file.estensione per salvare: ")
				if loc[-1] != os.sep: loc += os.sep
				fd = os.open(loc+recvfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0666)			
				indice=raw_input("Inserisci indice del file da scaricare: ")
				spegniRicerca=1
				IP=ricercheSuperPeer[int(indice)].IP
				Porta=ricercheSuperPeer[int(indice)].PORTA
				Filemd5=ricercheSuperPeer[int(indice)].FILEMD5	
				socketD=download(IP,Porta,Filemd5) 													#Creazione pacchetto RETR
																									#Risposta al download dal peer
				risposta=leggi(socketD,10)
				if not risposta:
					print "ERRORE RICEZIONE PACCHETTO DOWNLOAD DAL PEER"
					sys.exit(1)
				identificativo=risposta[0:4]
				if identificativo !="ARET":
					print "ERRORE RISPOSTA DOWNLOAD PEER"
				nChunk=int(risposta[4:10])  			
				conta=1	
				while conta <= nChunk:
					lenChunk=leggi(socketD,5)					
					lenChunk=int(lenChunk)	
					
					data=leggi(socketD,lenChunk)					
					os.write(fd, data)	
					conta=conta+1			
				print "Il file è stato salvato con successo!"			
				os.close(fd)			
				socketD.close() 
				
			if scelta=="4":																			#Stampo la lista dei super peer vicini
				stampaVicini(listaSuperPeer)
				
				
			if scelta=="5":																			#Stampo la lista dei peer collegati
				for i in listaLoggati.keys():
					print i," ",listaLoggati[i].IP," ",listaLoggati[i].PORTA
			if scelta=="6":
				for i in listaFile:					
					for id in i.SESSIONID:
						print i.FILENAME,"  ",id
			if scelta=="7":				
				ascolto.closeSocketACK()															#Chiudiamo la socket del threadAscolto
				print "...FINE...."
				break

if scelta=="2": 																					#PEER
	superPeer=0
	print "Salve peer....\n"
	scriviLog("NUOVA SESSIONE PEER")
	IP=raw_input("Inserisci IP del super peer ") 
	Porta=raw_input("Inserisci Porta del super peer  ") 
	IP=creaIP(IP) 
	Porta=controllaArgomentoNumero(5,Porta)
	listaVicini[0]=Vicini(IP,Porta)
	scriviLog("Primo vicino: "+IP+":"+Porta)
	ascolto=ThreadAscolto(PortaQuery)
	ascolto.start()
	scriviLog("Thread ascolto partito")
	
	
	if raw_input("Confermi il super peer?  [y/n] ").lower() == "y":
		TTL=raw_input("Inserisci Time to live (TTL) per i vicini: ")
		TTL=controllaDimensione(TTL)
		PKTID=generaPKTID(16)
		PKTID=controlla16B(16,PKTID)	
		pacchetto=supe(PKTID,mioIP,PortaQuery,TTL) 													#Creazione pacchetto SUPE
		try:
			print "Vicino 1: ",listaVicini[0].IP
			socketVicino1=creazioneSocket(listaVicini[0].IP,listaVicini[0].PORTA)
			socketVicino1.send(pacchetto)
			socketVicino1.close()
			print "Mandato SUPE al nodo 1."
			scriviLog("Inviato: "+pacchetto)
		except:
			print "Il nodo 1 si è disconnesso."
	
																									#LOGIN
	if raw_input("Login?  [y/n] ").lower() == "y":
		IPP2P=listaSuperPeer[0].IP	
		PortaP2P=listaSuperPeer[0].PORTA
		scriviLog("Provo a loggarmi ad "+IPP2P+" "+PortaP2P)
		peer_socket=creazioneSocket(IPP2P,"03000")
		peer_socket= logi(peer_socket,mioIP,PortaQuery)												#Connessione al peer di ascolto
		risposta=leggi(peer_socket,20) 
		if not risposta:
			print "ERRORE RICEZIONE PACCHETTO LOGIN: nessuna risposta"
			scriviLog("ERRORE RICEZIONE PACCHETTO LOGIN: nessuna risposta")
			sys.exit(1)
		identificativo=risposta[0:4]
		if identificativo !="ALGI":
			print "ERRORE RICEZIONE PACCHETTO LOGIN: no ALGI"
			scriviLog("ERRORE RICEZIONE PACCHETTO LOGIN: no ALGI")
			sys.exit(1)
		SessionID=risposta[4:len(risposta)] 														#Divido la risposta
		if SessionID=="0000000000000000":
			print "SessionID già presente"
			scriviLog("SessionID già presente")
			sys.exit(1)
		print "SEI LOGGATO"
		scriviLog("Loggato a "+IPP2P+" "+PortaP2P)
		peer_socket.close()
	

		indiceLista=0 																				#Indice della lista che salva i file che il peer aggiunge


		while 1:
			print
			print
			print "OPERAZIONI POSSIBILI:"
			print "1. aggiunta file;"
			print "2. rimozione file;"
			print "3. ricerca file;"
			print "4. download file;"
			print "5. Logout."
			
			scelta=raw_input("numero operazione: ")
			
			if scelta=="1": 																		#Aggiunta file
				peer_socket=creazioneSocket(IPP2P,"3000")
				print "aggiunta file in corso....."
				percorsoFile="./immagine/"				
				Filename=raw_input("Inserisci nome del file da aggiungere: ")
																									#Dal percorso del file recupero l'ultimo parametro che è il nome del file
				while not(esisteFile(percorsoFile+Filename)):
					Filename=raw_input("Inserisci nome del file da aggiungere: ")	
				Filemd5=creazioneFilemd5(percorsoFile+Filename) 									#Calcolo md5
				adff(peer_socket,SessionID,Filemd5,Filename) 										#Aggiunta file
				fileCondivisi[indiceLista]=FileCondivisi(percorsoFile+Filename,Filemd5)
				indiceLista=indiceLista+1				
																									#Attendo risposte sul server d'ascolto
				peer_socket.close()
		
			if scelta=="2" :																		#Rimozione file
				peer_socket=creazioneSocket(IPP2P,"3000")
				print "rimozione file in corso......."
				percorsoFile="./immagine/"
				Filename=raw_input("Inserisci nome del file.estensione da eliminare: ")
				Filemd5=creazioneFilemd5(percorsoFile+Filename)
				deff(peer_socket,SessionID,Filemd5)
																									#Attendo risposte sul server d'ascolto
				peer_socket.close()
			
			if scelta=="3": 																		#Ricerca file
				indice=0
				peer_socket=creazioneSocket(IPP2P,"3000")
 				print "ricerca file in corso....."
				Ricerca=raw_input("Inserisci stringa di ricerca del file: ")
				find(peer_socket,SessionID,Ricerca)
				peer_socket.shutdown(1)
				risposta=leggi(peer_socket,7)
				
				while not risposta:
					risposta=leggi(peer_socket,7)

				if not risposta:
					print "ERRORE RICEZIONE PACCHETTO AFIN"
				identificativo=risposta[0:4]
				if identificativo !="AFIN":
					print "ERRORE RISPOSTA IDENTIFICATIVO AFIN"
				nCopie=int(risposta[4:7])
				
				conta=1	
				print "Vengono stampati a video: "
				print "Filename IP Porta  "
				while nCopie>=conta:					
					risposta=leggi(peer_socket,119)							
					Filemd5=risposta[0:16]
					Filename=risposta[16:116]
					ncopy=risposta[116:119]
					conta=conta+1
					conta2=1
					stampa1=Filename.strip()
					while int(ncopy)>=conta2:					
						risposta=leggi(peer_socket,44)							
						IPP2PaltroPeer=risposta[0:39]
						PortaP2PaltroPeer=risposta[39:44]
						conta2=conta2+1
						stampa=str(indice)+") "+stampa1+" "+ IPP2PaltroPeer+" "+PortaP2PaltroPeer
						print stampa
						salvataggio[indice]=SalvaParametri(IPP2PaltroPeer,PortaP2PaltroPeer,Filemd5,Filename,0)					
						indice=indice+1
				
				peer_socket.close()

			if scelta== "4":																		#Download file
				print "download file in corso....."
				recvfn	= raw_input("Inserisci il nome del file.estensione per salvare: ")
				loc ="./fileScaricati/"
				fd = os.open(loc+recvfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0600)
				
				indice=raw_input("Inserisci indice del file da scaricare: ")
				IPP2PaltroPeer=salvataggio[int(indice)].IP
				PortaP2PaltroPeer=salvataggio[int(indice)].PORTA
				Filemd5=salvataggio[int(indice)].FILEMD5				
				peer_socketPeer=retr(IPP2PaltroPeer,PortaP2PaltroPeer,Filemd5)						#Dowload col peer
																									#Risposta al download dal peer
				rispostaPeer=leggi(peer_socketPeer,10)
				if not rispostaPeer:
					print "ERRORE RICEZIONE PACCHETTO DOWNLOAD DAL PEER"
					sys.exit(1)
				identificativoPeer=rispostaPeer[0:4]
				if identificativoPeer !="ARET":
					print "ERRORE RISPOSTA DOWNLOAD PEER"
				nChunk=int(rispostaPeer[4:10])
				
				conta=1	
				while conta <= nChunk:
					lenChunk=leggi(peer_socketPeer,5)					
					lenChunk=int(lenChunk)
					data=leggi(peer_socketPeer,lenChunk)						
					os.write(fd, data)	
					conta=conta+1
				print "Il file è stato salvato con successo!"
				
				os.close(fd)			
				peer_socketPeer.close()  															#Chiudo la socket con il peer da cui ho effettuato il download

			if scelta== "5": 																		#Logout
				peer_socket=creazioneSocket(IPP2P,"3000")
				print "logout....."
				logo(peer_socket,SessionID)
				scriviLog("Inviato LOGO"+SessionID)
																									#Risposta al logout
				risposta=leggi(peer_socket,7) 
				if not risposta:
					print "ERRORE RICEZIONE PACCHETTO LOGOUT"
					sys.exit(1)
				identificativo=risposta[0:4]
				if identificativo !="ALGO": 
					print "ERRORE RISPOSTA LOGOUT"
				print "Ricevuto ",risposta
				scriviLog("Ricevuto "+risposta)
				nCopieCancellate=risposta[4:len(risposta)]
				print "NUMERO COPIE CANCELLATE: ", nCopieCancellate
			
																									#Chiusura socket
				peer_socket.close()				
				ascolto.closeSocketACK()
				break
