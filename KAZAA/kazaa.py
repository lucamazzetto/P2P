#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#progetto3

#io  			fd00:0000:0000:0000:7ed1:c3ff:fe76:362a
#guerra 		fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
#mazzetto		fd00:0000:0000:0000:26fd:52ff:fe7a:6c5a

import socket,stat,sys,hashlib,os,threading,thread,time,re
from random import * 
import random
import string 
mioIP="fd00:0000:0000:0000:22c9:d0ff:fe47:70a3"
PortaQuery="03000"
#PortaQuery="3000"
gestioneRisposte={} #oggetto della classe threadRisposte
gestioneRisposte20s={}
listaVicini={} #lista degli ip e porte dei vicini
vicini={} #thread per fare query ai vicini

parametri={}
indiceListaSuperPeer=0
listaSuperPeer={} #lista dei super peer ricevuti dal pacchhetto asup
fileCondivisi={}
fileTrovati={}
spegniRicerca=0
superPeer=0 #variabile booleana per far capire nel thread ricerca se si è peer o super peer
listaPKTID={}  #lista dei PKTID dei quer che mi arrivano e ritrasmetto
listaPKTIDquer={}
listaPKTIDsupe={} #lista che salva i PKTID di tutti i pacchetti SUPE ricevuti
listaPKTIDquerFind={} #lista dei PKTID dei pacchetti QUER il superpeer trasmette dopo una FIND
listaPKTIDasup={}#lista dei pktid delle risposte asup
sessionidPKTID={}#lista che ha come indice il sessionId e ad ognuno è associato il pktid del pachetto quer che genera il superpeer quando arriva una find
salvataggio={} #lista dei parametri di afin
indice=0 #indice di "salvataggio" per il pacchetto afin
listaLoggati={} #lista dei peer che si sono loggati da noi
listaFile=[]# lista della tabella ADFF--> istanza della classe StrutturaFile
listaRispAque=[]#lista che contiene le risposte Aque
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
	PKTID=''
	# The constructor
	def __init__(self,IP, PORTA, FILEMD5,FILENAME,PKTID):		
		self.IP=IP
		self.PORTA=PORTA
		self.FILEMD5=FILEMD5
		self.FILENAME=FILENAME
		self.PKTID=PKTID
#--------------------------------------------------------------------------------------	
#FUNZIONI		
class Loggati: #tabella che salva il sessionId, ip e porta dei peer che si loggano a noi quando siamo super peer
	#SESSIONID=''
	IP=''
	PORTA=''
	# The constructor
	def __init__(self,IP, PORTA):		
		#self.SESSIONID=SESSIONID
		self.IP=IP
		self.PORTA=PORTA
def leggi(s,dim):
	dato=s.recv(dim)
	while len(dato)<dim:
		dato=dato+s.recv(1)
	return dato
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
	#print v		
	return str(v[0])+":"+str(v[1])+":"+str(v[2])+":"+str(v[3])+":"+str(v[4])+":"+str(v[5])+":"+str(v[6])+":"+str(v[7])
def elimina_asterischi(stringa):
        
        ritorno = ""
        ritorno2 = ""
        lettera = False
        lettera2 = False
        for i in range (0, len(stringa)):
            if(stringa[i] != "*" or lettera == True):
                ritorno = ritorno + stringa[i]
                lettera = True
       
        ritorno = ritorno[::-1]
    
        for i in range (0,len(ritorno)):
            if(ritorno[i]!="*" or lettera2==True):
                ritorno2=ritorno2+ritorno[i]
                lettera2 = True
    
        return ritorno2[::-1]
	
	
#stampa una lista
def stampa(l): 
	for elemento in l.keys():
		print elemento,l[elemento]
		
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
def cancellaPacchettiScaduti(lista,tempo,Tmax):
	for i in lista.keys():
			if tempo-lista[i] >= Tmax:
				del lista[i]		
	
def cancellaVicini(valore_da_cancellare,lista):
	i=valore_da_cancellare
	while(i<len(lista)-1):
		k=i+1
		lista[i]=lista[k]
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

def ricercaVicini(IP,Porta,lista):
	i=0
	while i < len(lista):
		if lista[i].IP==IP and lista[i].PORTA==Porta:  #se l'ip e la porta sono presenti
			return 0
		i=i+1
	return 1		
	
#CONTROLLO DIMENSIONE DELL'ARGOMENTO DEL PACCHETTO PACCHETTO
def controllaArgomentoNumero(dim,argomento): #aggiungo 0 davanti al numero se è troppo corto
	#if len(argomento) > dim :
		#print "FUNZIONE controllaArgomentoNumero-->Errore argomento troppo lungo.L'argomento viene troncato"
		#argomento=argomento[0:dim]
	if len(argomento) < dim :
		differenza=dim-len(argomento)
		i=0
		while i<differenza:
			argomento="0"+argomento
			i=i+1
	return argomento
	
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
	
def esisteFile(percorsoFile):
	try:
		fd=open(percorsoFile,"rb")		
		return 1
	except:
		print "Il file non esiste"
		return 0

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


def supe(PKTID,IP,PortaQuery,TTL):	
	pacchetto="SUPE"+PKTID+IP+PortaQuery+TTL
	return pacchetto
	
def asup(PKTID,IP,PortaQuery):	
	pacchetto="ASUP"+PKTID+IP+PortaQuery
	return pacchetto
	
def aque(PKTID,IP,P,Filemd5,Filename):	
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
	
def logi(peer_socket,IP,PORTA):	#login
	pacchetto="LOGI"+IP+PORTA
	peer_socket.send(pacchetto)
	return peer_socket	
	
	#LOGOUT:
def algi(peer_socket,SessionID):
	SessionID=controlla16B(16,SessionID)
	pacchetto="ALGI"+SessionID
	peer_socket.send(pacchetto)
def logo(peer_socket,SessionID):
	SessionID=controlla16B(16,SessionID)
	pacchetto="LOGO"+SessionID
	peer_socket.send(pacchetto)
	
def algo(peer_socket,n):
	pacchetto="ALGO"+n
	peer_socket.send(pacchetto)
def adff(peer_socket,SessionID,Filemd5,Filename): #aggiunta file
	Filemd5=controlla16B(16,Filemd5)
	Filename=controllaArgomentoStringa(100,Filename)
	SessionID=controlla16B(16,SessionID)
	pacchetto="ADFF"+SessionID+Filemd5+Filename
	peer_socket.send(pacchetto)
	
def deff(peer_socket,SessionID,Filemd5): #rimozione file
	Filemd5=controlla16B(16,Filemd5)
	SessionID=controlla16B(16,SessionID)
	pacchetto="DEFF"+SessionID+Filemd5
	peer_socket.send(pacchetto)
	
def find(peer_socket,SessionID,Ricerca): #ricerca rivolta dal peer al super peer
	SessionID=controlla16B(16,SessionID)
	Ricerca=controllaArgomentoStringa(20,Ricerca)
	pacchetto="FIND"+SessionID+Ricerca
	peer_socket.send(pacchetto)
	
def retr(IPP2P,PortaP2P,Filemd5):	
	peer_socketPeer = creazioneSocket(IPP2P,PortaP2P)
	Filemd5=controlla16B(16,Filemd5)
	pacchetto="RETR"+Filemd5
	peer_socketPeer.send(pacchetto)
	return 	peer_socketPeer


#------------------------------------------------------------------

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
			#listaVicini=cancellaVicini(self.i,listaVicini)

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
	acceso=1
	def __init__(self,Porta):
		threading.Thread.__init__(self)		
		self.porta=Porta		
	def run(self):
		# Create the socket
		try:
			self.socketACK=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.socketACK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socketACK.bind(("", int(self.porta)))
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
		self.socketACK.settimeout(100)
		while self.acceso:
			
			try:				
				(conn, addr) = self.socketACK.accept()
				cid=addr[0]
				#print "cid: ",cid									
				gestioneRisposte[cid]=threadRisposte(cid, conn,self)
				gestioneRisposte[cid].start()
			except socket.timeout:
				print "Tempo scaduto.....cancellazione pacchetti in corso.."	
				tempo=time.time()
				cancellaPacchettiScaduti(listaPKTID,tempo,500) #lista pktid:pktid dei quer che ritrasmetto
				cancellaPacchettiScaduti(listaPKTIDsupe,tempo,500)#lista pktidsupe:pktid dei supe che ritrasmetto
				#cancellaPacchettiScaduti(PKTIDmio,tempo,20)
				print				
				print 
				#cancellaPacchettiScaduti(PKTIDmio,tempo)
				self.socketACK.settimeout(100)
				#client_socket.send("tempo scaduto")		
	def log(self, msg):
		print(msg)
	def closeSocketACK(self):
		try:
			self.acceso=0
			self.socketACK.close()
			return True
		except:
			self.log('Cannot close socketACK')
			return False
	
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
		self.socketACK.setblocking(1)
		self.server=server
	# The running method
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
		identificativo=leggi(self.socketACK,4)#146B per ogni riga
		if not identificativo:
			print "ERRORE RICEZIONE identificativo threadRisposte"
			sys.exit(1)					
		if identificativo !="RETR" and identificativo !="ASUP" and identificativo !="SUPE" and identificativo !="QUER" and identificativo !="FIND" and identificativo !="LOGI" and identificativo !="ADFF" and identificativo !="DEFF" and identificativo !="LOGO":
			print "ERRORE RISPOSTA IDENTIFICATIVO ASUP, SUPE,QUER,FIND..."
			self.socketACK.close()	
				
		if identificativo =="RETR":					
			Filemd5=leggi(self.socketACK,16)	
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
			self.socketACK.send(pacchetto) 
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
			if superPeer==0: #sono un peer
				if listaPKTIDasup.has_key(PKTID)==0: #pktid non presente nella lista
					print "Pacchetto ASUP ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro
					scriviLog("Ricevuto ASUP dal peer "+ self.id+" : "+PKTID+" "+IPparametro+" "+Portaparametro)
					listaPKTIDasup[PKTID]=time.time()					
					listaSuperPeer[indiceListaSuperPeer]=Vicini(IPparametro,Portaparametro)	
					scriviLog("Super Peer aggiunto: "+IPparametro+" "+Portaparametro)				
				else:
					scriviLog("!!Pacchetto Scartato!!!! ASUP"+pacchettoR+" ricevuto del peer"+ip)
			
			if superPeer==1: #sono un super peer
				if ricercaVicini(IPparametro,Portaparametro,listaSuperPeer) ==1: #se super non è presente nella listaSuperPeer				
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
			if listaPKTIDsupe.has_key(PKTID) == 0 : #pktid non esistente
				listaPKTIDsupe[PKTID]=time.time()				
				print "Pacchetto SUPE ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",TTL
				scriviLog("Ricevuto SUPE da "+self.id+" : "+IPparametro+":"+Portaparametro+" TTL:"+TTL)	
				#print "TTL ",TTL
				if superPeer==1: #se sono un super peer rispondo con ASUP					
					if IPparametro!=mioIP:
						pacchetto=asup(PKTID,mioIP,PortaQuery)
						v=threadRicerca(IPparametro,Portaparametro,pacchetto,-1)
						v.start()
						scriviLog("Invio "+pacchetto+" Vicino "+IPparametro+":"+Portaparametro)	
				if(int(TTL)>1):  #invio di nuovo il pacchetto
					#print "dentro if(ttl)"
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)	
					pacchetto=supe(PKTID,IPparametro,Portaparametro,TTL)						
					i=0
					#print "len(listaVicini): ",len(listaVicini)
					#print "listavicini: ",listaVicini
					while i< len(listaVicini): #indiceLista è l'indice per scorrere la lista dei vicini 
						#print "while --> vicini: ",listaVicini
						if(listaVicini[i].IP != IPparametro and listaVicini[i].IP !=ip):
							#print "if"
						#if((listaVicini[i].IP != IPparametro and listaVicini[i].PORTA != Portaparametro) and listaVicini[i].IP !=ip): #controllo per non rinviare il pacchetto a chi me lo ha inviato
							vicini[i]=threadRicerca(listaVicini[i].IP,listaVicini[i].PORTA,pacchetto,i) #ritrasmetto il pacchetto
							vicini[i].start()	
							scriviLog("Invio "+pacchetto+" Vicino "+listaVicini[i].IP+":"+listaVicini[i].PORTA)													
						i=i+1	
				
			else:
				scriviLog("!!Pacchetto Scartato!!!! "+pacchettoR+" ricevuto del peer"+ip)
			
			
					
		if identificativo =="QUER":
			ip=creaIP(self.id)
			#print "ip: ",ip
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
			#print "Pacchetto QUER ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",Ricerca," ",TTL	
			if listaPKTID.has_key(PKTID)==0: #pktid non esistente
				print "Pacchetto QUER ricevuto dal peer ", self.id," : ",PKTID," ",IPparametro," ",Portaparametro," ",Ricerca," ",TTL	
				scriviLog("Pacchetto QUER ricevuto dal peer "+ self.id+" : "+PKTID+" "+IPparametro+" "+Portaparametro+" "+Ricerca+" "+TTL)	
				listaPKTID[PKTID]=time.time()				
				if(int(TTL)>1):  #invio di nuovo il pacchetto
					TTL=str(int(TTL)-1)
					TTL=controllaDimensione(TTL)						
					pacchetto=query(PKTID,IPparametro,Portaparametro,TTL,Ricerca)
					i=0
					while i< len(listaSuperPeer): #indiceLista è l'indice per scorrere la lista dei vicini 		
						#print "vicino ",listaVicini[i].IP,listaVicini[i].PORTA
						if(listaSuperPeer[i].IP != IPparametro and listaSuperPeer[i].IP != ip): #controllo per non rinviare il pacchetto a chi me lo ha inviato
							vicini[i]=threadRicerca(listaSuperPeer[i].IP,listaSuperPeer[i].PORTA,pacchetto,i) #ritrasmetto il pacchetto
							vicini[i].start() 	
							scriviLog("Invio "+pacchetto+" Vicino "+listaSuperPeer[i].IP+":"+listaSuperPeer[i].PORTA)							
						i=i+1
			
				#CERCO I MATCH NELLA MIA listaFile E LI SALVO IN listaRispAque
				p=re.compile(Ricerca,re.IGNORECASE)
				for i in listaFile:
					#print "i.FILENAME:",i.FILENAME
					#print "i.FILEMD5:",i.FILEMD5
					#print "p.search(i.FILENAME) ",p.search(i.FILENAME)
					if p.search(i.FILENAME): #se c'è
						#print "l'ho trovato!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
						
						for l in i.SESSIONID:
							FILENAME=controllaArgomentoStringa(100,i.FILENAME)
							pacchetto=aque(PKTID,listaLoggati[l].IP,listaLoggati[l].PORTA,i.FILEMD5,FILENAME)
							try:
								socketAQUE=creazioneSocket(IPparametro,Portaparametro)							
							except:
								self.log('Cannot connect the socketAQUE.')
								return False	
							#filename=controllaArgomentoStringa(100,fileTrovati[k])
							
							socketAQUE.send(pacchetto)	
												
							socketAQUE.close()
							scriviLog("Invio "+pacchetto+" Vicino "+IPparametro+":"+Portaparametro)							
			else:
				scriviLog("!!!!!Pacchetto scartato "+pacchettoR+" Ricevuto dal peer "+ip)		
		
		########################
			
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
			if superPeer==1: #sono superpeer
				PKTID=generaPKTID(16)
				sessionidPKTID[PKTID]=SessionID
				#TTL
#DA RICONTRALLARE
				TTL="03"#raw_input("Inserisci Time to live (TTL) per inviare la quer: ")
				TTL=controllaDimensione(TTL)
				PortaAscolto20s=randint(40000,60000)
				pacchettoQUER=query(PKTID,mioIP,str(PortaAscolto20s),TTL,Ricerca)
				listaPKTIDquerFind[PKTID]=time.time()
				
				#CERCO I MATCH NELLA MIA listaFile E LI SALVO IN listaRispAque
				p=re.compile(Ricerca,re.IGNORECASE)
				for i in listaFile:
					#print "i.FILENAME:",i.FILENAME
					#print "i.FILEMD5:",i.FILEMD5
					#print "p.search(i.FILENAME) ",p.search(i.FILENAME)
					if p.search(i.FILENAME): #se c'è
						#print "l'ho trovato!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
						if listaPKTIDquerFind.has_key(PKTID) == 1: #se è presente
							trovatoPKTID=0
							#for indice in listaRispAque.keys():
							for indice in listaRispAque:
								#print "SONO DENTRO:",indice.PKTID
								if indice.PKTID==PKTID:
									trovatoPKTID=1
									#indicetrovato=indice
									break
									
							if trovatoPKTID==1:
								trovatoMD5=0
								#print "dentro if trovatoPKTID==1:"
								for chiave in indice.LISTA:#indicetrovato.LISTA:
									if chiave.FILEMD5==i.FILEMD5:
										trovatoMD5=1
										#print "file md5 presente"
										break	
								#print "trovatoMD5= ",trovatoMD5
								if trovatoMD5==1:
									#print "dentro"
									for s in range(len(i.SESSIONID)):
										#print "mio SESSIONID: ",SessionID,"i.SESSIONID[s]: ",i.SESSIONID[s]
										if SessionID != i.SESSIONID[s]:
											chiave.LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
								else:
									if SessionID != i.SESSIONID[0]:
										indice.LISTA.append(creaLISTA(i.FILEMD5,i.FILENAME, listaLoggati[i.SESSIONID[0]].IP,listaLoggati[i.SESSIONID[0]].PORTA))
										#print "non ho trovato filmd5 aggiungo una nuova riga al pktid"
										for s in range(1,len(i.SESSIONID)):
											if SessionID != i.SESSIONID[s]:
											#print "dentro s:",s
											#print "len(indice.lista)",len(indice.LISTA)," ", listaLoggati[i.SESSIONID[s]].IP," ",listaLoggati[i.SESSIONID[s]].PORTA
												indice.LISTA[len(indice.LISTA)-1].LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
									else:
										if len(i.SESSIONID)!=1:
											indice.LISTA.append(creaLISTA(i.FILEMD5,i.FILENAME, listaLoggati[i.SESSIONID[1]].IP,listaLoggati[i.SESSIONID[1]].PORTA))
											#print "non ho trovato filmd5 aggiungo una nuova riga al pktid"
											for s in range(2,len(i.SESSIONID)):
												if SessionID != i.SESSIONID[s]:
												#print "dentro s:",s
												#print "len(indice.lista)",len(indice.LISTA)," ", listaLoggati[i.SESSIONID[s]].IP," ",listaLoggati[i.SESSIONID[s]].PORTA
													indice.LISTA[len(indice.LISTA)-1].LISTAIPPORTA.append(creaLISTAIPPORTA(listaLoggati[i.SESSIONID[s]].IP,listaLoggati[i.SESSIONID[s]].PORTA))
									
							else:
								#print "il pktid non è ancora presente"
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
								#print "listaRispAque: ",listaRispAque
				#AVVIO IL THREAD CHE ASPETTA LE AQUE
				s=ThreadAscolto20s(PortaAscolto20s)
				s.start()
												
				#PROPAGO LA RICHIESTA QUER AI SUPERPEER
				k=0
				while k< len(listaSuperPeer): 
						try:
							socketFIND=creazioneSocket(listaSuperPeer[k].IP,listaSuperPeer[k].PORTA)							
						except:
							self.log('Cannot connect the socketFIND.')
							return False	
						#filename=controllaArgomentoStringa(100,fileTrovati[k])						
						socketFIND.send(pacchettoQUER)	
						k=k+1						
						socketFIND.close()
						scriviLog("Invio "+pacchettoQUER+" Vicino "+listaSuperPeer[k-1].IP+":"+listaSuperPeer[k-1].PORTA)	
				s.join(20)
				s.closeSocketAscolto20s()
				s.stop()
				print "Sono scaduti i 20sec"					
							
				for i in listaRispAque: #scorro i PKTID
					#print "\nstampo i ",i.PKTID						
					if PKTID==i.PKTID:	
						numMD5="%03d" % len(i.LISTA)
						pacchetto="AFIN"+ numMD5
						pacchettoPrint="AFIN "+ numMD5+"\n"
						#print "pacchetto",pacchetto
						for k in i.LISTA: #scorro gli MD5
							FILENAME=controllaArgomentoStringa(100,k.FILENAME)
							numIPPORTA="%03d" % len(k.LISTAIPPORTA)
							pacchetto= pacchetto+k.FILEMD5+FILENAME+numIPPORTA
							pacchettoPrint=pacchettoPrint+" "+FILENAME.strip()+" "+numIPPORTA
							for ipp in k.LISTAIPPORTA: #scorro gli IP e le PORTE
								pacchetto= pacchetto+ipp.IP+ipp.PORTA
								pacchettoPrint=pacchettoPrint+" ip:"+ipp.IP+" porta:"+ipp.PORTA+"\n"
						scriviLog("Inviato "+pacchetto)
						print pacchettoPrint
				print pacchetto					
				self.socketACK.send(pacchetto)				
				
				listaPKTIDquerFind={} #azzero la lista listaPKTIDquerFind				
				print
				print			
				#print "sono arrivata alla fine!!!!!!"					
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
			if superPeer==1: #sono super peer
				#controllo che ip e porta non siano gia presenti nella listaLoggati
				peerPresente=0 #il peer non si era ancora loggato
				for chiave in listaLoggati.keys():
					if IPparametro==listaLoggati[chiave].IP and Portaparametro==listaLoggati[chiave].PORTA:
						peerPresente=1 #peer gia loggato
						SessionID="0000000000000000"
						scriviLog("Peer già loggato")	
						break
				if peerPresente==0:	
					SessionID=generaPKTID(16) #genero il sessionID
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
			if superPeer==1: #sono super peer				
				if listaLoggati.has_key(SessionID): #controllo che il SessionID sia loggato (Se la chiave SessionID è presente)		
					filePresente=0
					for files in listaFile:	#controllo che non sia già presente il filemd5
						if files.FILEMD5==Filemd5: #se il filemd5 è presente allora lo rinomino
							filePresente=1
							files.FILENAME=Filename
							trovato=0
							for id in range(len(files.SESSIONID)): #controllo che il SessionID che ha aggiunto il file è gia presente
								if files.SESSIONID[id]==SessionID:	
									trovato=1
									break 
							if trovato==0: #sessionId non presente	
								files.SESSIONID.append(SessionID) #aggiungo il SessionID per il filemd5 inserito
					if filePresente==0: #il filemd5 non è presente nella tabella
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
			if superPeer==1: #sono super peer	
				if listaLoggati.has_key(SessionID): #controllo che il SessionID sia loggato (Se la chiave SessionID è presente)	
					print "Ricevuto pacchetto "+pacchettoR+" da utente "+ip
					for file in listaFile:
						if file.FILEMD5==Filemd5:
							file.SESSIONID.remove(SessionID) #cancello il SessionID-->quel SessionID non è più associato a quel filemd5
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
			if superPeer==1: #sono super peer	
				if listaLoggati.has_key(SessionID): #controllo che il SessionID sia loggato (Se la chiave SessionID è presente)	
					nCancellati=0
					#print "len(listaFILE)",str(len(listaFile))
														
					for file in listaFile:					
						#print "len(file.SESSIONID) ",str(len(file.SESSIONID))
						#print file.FILENAME
						for i in range(len(file.SESSIONID)):
							#print "DENTROOOOOOOOOO"
							if file.SESSIONID[i]==SessionID:
								file.SESSIONID.pop(i) 
								nCancellati=nCancellati+1
					for file in range(len(listaFile),0):
						#print len(listaFile[file].SESSIONID)
						if len(listaFile[file].SESSIONID) == 0:
							#print "Rimuovo ",listaFile[file].FILENAME
							listaFile.pop(file)
					
					nCancellati=controllaArgomentoNumero(3,str(nCancellati))
					algo(self.socketACK,nCancellati)
					#listaLoggati.remove(SessionID)
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

		# Destroy from the server this client?
		if not nodestroy:
			del self.server.gestioneRisposte[self.id]

	# Log. By default it uses the server class
	def log(self, msg):
		self.server.log('Client '+self.id+': '+msg)			
class ThreadAscolto20s(threading.Thread):
	ip=""
	porta=""	
	maxconn=5	
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
		# Create the socket
		try:
			self.socketAscolto20s=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		except:
			print "errore socket"
		try:
			self.socketAscolto20s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except:
			print "errore socketopt"
		try:
			self.socketAscolto20s.bind(("", int(self.porta)))
			#print ('la socket è creata.')
		except:
			self.log('Cannot bind the socketAscolto20s.')
			return False

		# Listen on it
		try:
			self.socketAscolto20s.listen(self.maxconn)
			#print ('la socket è in ascolto.')
		except:
			self.log('Cannot listen on the socketAscolto20s.')
			return False	
	
		while self.acceso:			
			try:				
				(conn,addr) = self.socketAscolto20s.accept()
				cid=addr[0]
				gestioneRisposte20s[cid]=threadRisposte20s(cid, conn,self)
				gestioneRisposte20s[cid].start()
			except:
				print "Errore nell'accept del ThreadAscolto20s"
				############################EROQUI
				
	def log(self, msg):
		print(msg)
	def closeSocketAscolto20s(self):
		try:
			self.socketAscolto20s.close()
			return True
		except:
			self.log('Cannot close socketAscolto20s')
			return False
	def stop(self):
		self.acceso=0
			
		
									
class threadRisposte20s(threading.Thread): 
	# The id of the client
	id=''
	# The connection
	socketRisposte20s=None	
	receive=1
	# The server instance
	server=None
	# The constructor
	def __init__(self, id, socket, server):
		threading.Thread.__init__(self)
		self.id=id
		self.socketRisposte20s=socket
		self.server=server		
		

	# The running method
	def run(self):	
					
		global listaPKTID
		global listaPKTIDsupe
		global listaVicini
		global spegniRicerca		
		global listaSuperPeer
		global indiceListaSuperPeer
		global salvataggio #lista dei parametri di afin
		global indice 
		global listaRispAque
		identificativo=leggi(self.socketRisposte20s,4)#146B per ogni riga
		#print identificativo
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
			
			if listaPKTIDquerFind.has_key(PKTID) == 1 or listaPKTIDquer.has_key(PKTID) == 1: #se è presente
				trovatoPKTID=0
				#for indice in listaRispAque.keys():
				for indice in listaRispAque:
					#print "SONO DENTRO:",indice.PKTID
					if indice.PKTID==PKTID:
						trovatoPKTID=1
						break
						
				if trovatoPKTID==1:
					trovatoMD5=0
					for chiave in indice.LISTA:
						if chiave.FILEMD5==Filemd5:
							trovatoMD5=1
							#print "file md5 presente"
							break	
							
					if trovatoMD5==1:
						for s in range(len(chiave.LISTAIPPORTA)):
							if chiave.LISTAIPPORTA!=IPparametro:
								chiave.LISTAIPPORTA.append(creaLISTAIPPORTA(IPparametro,Portaparametro))
					else:
						indice.LISTA.append(creaLISTA(Filemd5,Filename, IPparametro,Portaparametro))
						#print "non ho trovato filmd5 aggiungo una nuova riga al pktid"
						
				else:
					#print "il pktid non è ancora presente"
					listaRispAque.append(creaListaRispAque(PKTID,Filemd5,Filename, IPparametro,Portaparametro))															
					
				
			else:
				print "Il pacchetto AQUE ricevuto non corrisponde a una nostra richiesta."
									
	def close(self, nodestroy=False):
		self.log('Disconnetting')
		self.receive=0
		self.socketRisposte20s.close()

		# Destroy from the server this client?
		if not nodestroy:
			del self.server.gestioneRisposte20s[self.id]

	# Log. By default it uses the server class
	def log(self, msg):
		self.server.log('Client '+self.id+': '+msg)					
#-----------------------------------------------------------------------------------------
#Main----------------------------------
print "PROGETTO 3... Scegli cosa vuoi essere:"
print "1. SUPER peer,"
print "2. peer,"
scelta=raw_input("Numero scelta: \n")

if scelta=="1": #SUPER PEER
	superPeer=1
	print "Salve super peer...\n"
	scriviLog("NUOVA SESSIONE super PEER")
	IP=raw_input("Inserisci IP Super peer vicino: ") 
	Porta=raw_input("Inserisci Porta Super peer vicino: ") 
	IP=creaIP(IP) 
	Porta=controllaArgomentoNumero(5,Porta)
	listaVicini[0]=Vicini(IP,Porta)
	scriviLog("Primo vicino: "+IP+":"+Porta)

	#IP=raw_input("Inserisci IP vicino 2: ") 
	#Porta=raw_input("Inserisci Porta vicino 2: ") 
	#Porta=controllaArgomentoNumero(5,Porta)
	#IP=creaIP(IP)  
	#listaVicini[1]=Vicini(IP,Porta)
	#scriviLog("Secondo vicino: "+IP+":"+Porta)
	SalvaFile() #salvo i filemd5 e filename che voglio condividere
	lista=(os.listdir('./immagine')	)
	i=0
	while i <len(lista):
		percorso="./immagine/"+lista[i]
		filemd5=creazioneFilemd5(percorso)
		#NOI NON AVREMO MAI DUE NOMI DIVERSI CON LO STESSO MD5!!!!
		listaFile.append(StrutturaFile(filemd5,lista[i],"00000000000000ME"))
		i=i+1
	
	listaLoggati["00000000000000ME"]=Loggati(mioIP,PortaQuery)
	
	j=0
	#faccio partire il thread del server per stare in ascolto di possibili download
	
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
			print "2. ricerca super peer;"
			print "3. download file;"
			print "4. stampa super peer vicini;"
			print "5. stampa peer collegati;"
			print "6. stampa tutti i file caricati"
			print "7. esci."
			
			
			scelta=raw_input("Numero operazione: \n")

			
			if scelta=="1": #ricerca file
				spegniRicerca=0
				ricercheSuperPeer=[]						
				TTL=raw_input("Inserisci Time to live (TTL): ")
				TTL=controllaDimensione(TTL)
				Ricerca=raw_input("Inserisci la stringa di ricerca: ") #il controllo della lunghezza di Ricerca è dentro alla funzione query			
				PKTID=generaPKTID(16)
				PKTID=controlla16B(16,PKTID)
				listaPKTIDquer[PKTID]=time.time()  #ci salviamo il PKTID che mandiamo
				j=j+1
				PortaAscolto20s=randint(40000,60000)
				pacchetto=query(PKTID,mioIP,str(PortaAscolto20s),TTL,Ricerca) #costruisco il pacchetto QUER
				s=ThreadAscolto20s(PortaAscolto20s)
				s.start()
				i=0			
				while i< len(listaSuperPeer):		#inviamo il pacchetto QUER a tutti i vicini			
					vicini[i]=threadRicerca(listaSuperPeer[i].IP,listaSuperPeer[i].PORTA,pacchetto,i)
					vicini[i].start()
					scriviLog("Invio "+pacchetto+"  Al superpeer "+listaSuperPeer[i].IP+":"+listaSuperPeer[i].PORTA)
					i=i+1	
				s.join(20)
				s.stop()
			
				
				
				p=re.compile(Ricerca.strip(),re.IGNORECASE)
				for i in listaFile:
					#print "i.FILENAME:",i.FILENAME
					#print "i.FILEMD5:",i.FILEMD5
					#print "p.search(i.FILENAME) ",p.search(i.FILENAME)
					if p.search(i.FILENAME): #se c'è
						#print "l'ho trovato!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
						for l in i.SESSIONID:
							if l!="00000000000000ME":
								ricercheSuperPeer.append(SalvaParametri(listaLoggati[l].IP,listaLoggati[l].PORTA,i.FILEMD5,i.FILENAME,PKTID))
				#ora stampo a video da listaPKTIDquer che sono i risultati del super peer
				for j in listaPKTIDquer.keys(): 
					for i in listaRispAque: #scorro i PKTID
						if j==i.PKTID:				
							for k in i.LISTA: #scorro gli MD5
								for ipp in k.LISTAIPPORTA: #scorro gli IP e le PORTE
									ricercheSuperPeer.append(SalvaParametri(ipp.IP,ipp.PORTA,k.FILEMD5,k.FILENAME,i.PKTID))
				j=0
				for i in ricercheSuperPeer:
					print j,") ",i.FILENAME," ",i.IP," ",i.PORTA
					j=j+1
				listaPKTIDquer={}	#azzero la lista listaPKTIDquer	
				
			if scelta=="2" :#ricerca superpeer		
				listaSuperPeer={}
				TTL=raw_input("Inserisci Time to live (TTL) per i vicini: ")
				TTL=controllaDimensione(TTL)
				PKTID=generaPKTID(16)
				PKTID=controlla16B(16,PKTID)	
				pacchetto=supe(PKTID,mioIP,PortaQuery,TTL) #creazione pacchetto NEAR
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
				
			if scelta=="3": #download file			
				print "download file in corso....."
				loc="./fileScaricati/"
				recvfn	= raw_input("Inserisci il nome del file.estensione per salvare: ")
				#loc = raw_input("In che cartella salvare? ")
				if loc[-1] != os.sep: loc += os.sep
				fd = os.open(loc+recvfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0666)			
				indice=raw_input("Inserisci indice del file da scaricare: ")
				spegniRicerca=1
				IP=ricercheSuperPeer[int(indice)].IP
				Porta=ricercheSuperPeer[int(indice)].PORTA
				Filemd5=ricercheSuperPeer[int(indice)].FILEMD5
				#Filename=parametri[int(indice)].FILENAME			
				socketD=download(IP,Porta,Filemd5) #creazione pacchetto RETR
				#risposta al download dal peer
				risposta=leggi(socketD,10) #impostare bene le dimensioni
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
					lenChunk=leggi(socketD,5)					
					lenChunk=int(lenChunk)	
					
					data=leggi(socketD,lenChunk)					
					os.write(fd, data)	
					conta=conta+1			
				print "Il file è stato salvato con successo!"			
				os.close(fd)			
				socketD.close() 
				
			if scelta=="4":#stampo la lista dei super peer vicini
				stampaVicini(listaSuperPeer)
				
				
			if scelta=="5":#stampo la lista dei peer collegati
				for i in listaLoggati.keys():
					print i," ",listaLoggati[i].IP," ",listaLoggati[i].PORTA
			if scelta=="6":
				for i in listaFile:					
					for id in i.SESSIONID:
						print i.FILENAME,"  ",id
			if scelta=="7":				
				ascolto.closeSocketACK()#chiudiamo la socket del threadAscolto
				print "...FINE...."
				break

if scelta=="2": #PEER
	superPeer=0
	print "Salve peer....\n"
	scriviLog("NUOVA SESSIONE PEER")
	IP=raw_input("Inserisci IP del super peer ") 
	Porta=raw_input("Inserisci Porta del super peer  ") 
	IP=creaIP(IP) 
	Porta=controllaArgomentoNumero(5,Porta)
	listaVicini[0]=Vicini(IP,Porta)
	scriviLog("Primo vicino: "+IP+":"+Porta)

	#IP=raw_input("Inserisci IP vicino 2: ") 
	#Porta=raw_input("Inserisci Porta vicino 2: ") 
	#Porta=controllaArgomentoNumero(5,Porta)
	#IP=creaIP(IP)  
	#listaVicini[1]=Vicini(IP,Porta)
	#scriviLog("Secondo vicino: "+IP+":"+Porta)
	ascolto=ThreadAscolto(PortaQuery)
	ascolto.start()
	scriviLog("Thread ascolto partito")
	
	
	if raw_input("Confermi il super peer?  [y/n] ").lower() == "y":
		TTL=raw_input("Inserisci Time to live (TTL) per i vicini: ")
		TTL=controllaDimensione(TTL)
		PKTID=generaPKTID(16)
		PKTID=controlla16B(16,PKTID)	
		pacchetto=supe(PKTID,mioIP,PortaQuery,TTL) #creazione pacchetto SUPE
		try:
			print "Vicino 1: ",listaVicini[0].IP
			socketVicino1=creazioneSocket(listaVicini[0].IP,listaVicini[0].PORTA)	
			#socketVicino2=creazioneSocket(listaVicini[1].IP,listaVicini[1].PORTA)	
			socketVicino1.send(pacchetto)
			#socketVicino2.send(pacchetto)	
			socketVicino1.close()
			print "Mandato SUPE al nodo 1."
			scriviLog("Inviato: "+pacchetto)
			#socketVicino2.close()
		except:
			print "Il nodo 1 si è disconnesso."
		#try:
		#	print "Vicino 2: ",listaVicini[1].IP
		#	socketVicino2=creazioneSocket(listaVicini[1].IP,listaVicini[1].PORTA)	
		#	socketVicino2.send(pacchetto)	
		#	socketVicino2.close()
		#	print "Mandato SUPE al nodo 2."
		#	scriviLog("Inviato: "+pacchetto)
		#except:
		#	print "Il nodo 2 si è disconnesso."	
	
	#LOGIN:
	if raw_input("Login?  [y/n] ").lower() == "y":
		#OPERAZIONI DI LOGIN
		
		#mi connetto al super peer scelto
		IPP2P=listaSuperPeer[0].IP	
		PortaP2P=listaSuperPeer[0].PORTA
		scriviLog("Provo a loggarmi ad "+IPP2P+" "+PortaP2P)
		#peer_socket=creazioneSocket(IPP2P,PortaP2P)
		peer_socket=creazioneSocket(IPP2P,"03000")  ###########################################
		peer_socket= logi(peer_socket,mioIP,PortaQuery)	
		#risposta al login
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
		SessionID=risposta[4:len(risposta)] #divide la risposta per ogni punto in un vettore di stringhe[0 1 2]:prendiamo l'ultimo
		if SessionID=="0000000000000000":
			print "SessionID già presente"
			scriviLog("SessionID già presente")
			sys.exit(1)
		print "SEI LOGGATO"
		scriviLog("Loggato a "+IPP2P+" "+PortaP2P)
		peer_socket.close()
		# Create the instance
	

		indiceLista=0 #indice della lista che salva i file che il peer aggiunge


		while 1:
			print
			print
			print "OPERAZIONI POSSIBILI:"
			#print "0. Login;"
			print "1. aggiunta file;"
			print "2. rimozione file;"
			print "3. ricerca file;"
			print "4. download file;"
			print "5. Logout."
			
			scelta=raw_input("numero operazione: ")

			#if scelta=="0": #LOGIN
			
			if scelta=="1": #aggiunta file
				#peer_socket=creazioneSocket(IPP2P,PortaP2P)
				peer_socket=creazioneSocket(IPP2P,"3000") ##################################
				print "aggiunta file in corso....."
				percorsoFile="./immagine/"				
				Filename=raw_input("Inserisci nome del file da aggiungere: ")				
				#Filename=percorsoFile.split(os.sep)[-1] #dal percorso del file recupero l'ultimo parametro che è il nome del file
				while not(esisteFile(percorsoFile+Filename)):
					Filename=raw_input("Inserisci nome del file da aggiungere: ")	
				Filemd5=creazioneFilemd5(percorsoFile+Filename) #calcolo md5
				adff(peer_socket,SessionID,Filemd5,Filename) #aggiunta file
				fileCondivisi[indiceLista]=FileCondivisi(percorsoFile+Filename,Filemd5)
				indiceLista=indiceLista+1				
#attendo risposte sul server d'ascolto
				peer_socket.close()
		#...........................................................................................................		
			if scelta=="2" :#rimozione file
				#peer_socket=creazioneSocket(IPP2P,PortaP2P)
				peer_socket=creazioneSocket(IPP2P,"3000")  ########################################
				print "rimozione file in corso......."
				percorsoFile="./immagine/"
				Filename=raw_input("Inserisci nome del file.estensione da eliminare: ")
				#Filename=percorsoFile.split(os.sep)[-1] #dal percorso del file recupero l'ultimo parametro che è il nome del file
				Filemd5=creazioneFilemd5(percorsoFile+Filename) #calcolo md5
				deff(peer_socket,SessionID,Filemd5)
#attendo risposte sul server d'ascolto
				peer_socket.close()
			#....................................................................................	
			
			if scelta=="3": #ricerca file
				indice=0
				#peer_socket=creazioneSocket(IPP2P,PortaP2P)
				peer_socket=creazioneSocket(IPP2P,"3000")  #############################################
 				print "ricerca file in corso....."
				Ricerca=raw_input("Inserisci stringa di ricerca del file: ")
				find(peer_socket,SessionID,Ricerca)
				#ascolto20s=ThreadAscolto20s(PortaAscolto20s)
				#ascolto20s.start()
#RISPOSTA AFIN:va messo nel thread
				peer_socket.shutdown(1)
				risposta=leggi(peer_socket,7)#146B per ogni riga
				
				while not risposta:
					risposta=leggi(peer_socket,7)

				
				
				#print "ho letto",risposta,"."
				if not risposta:
					print "ERRORE RICEZIONE PACCHETTO AFIN"
					#sys.exit(1)
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
			#.........................................................................................	
			if scelta== "4":#download file
				print "download file in corso....."
				recvfn	= raw_input("Inserisci il nome del file.estensione per salvare: ")
				loc ="./fileScaricati/" #raw_input("In che cartella salvare? ")
				#if loc[-1] != os.sep: loc += os.sep
				fd = os.open(loc+recvfn, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0600)
				
				indice=raw_input("Inserisci indice del file da scaricare: ")
				IPP2PaltroPeer=salvataggio[int(indice)].IP
				PortaP2PaltroPeer=salvataggio[int(indice)].PORTA
				Filemd5=salvataggio[int(indice)].FILEMD5				
				peer_socketPeer=retr(IPP2PaltroPeer,PortaP2PaltroPeer,Filemd5)#dowload col peer
				#risposta al download dal peer
				rispostaPeer=leggi(peer_socketPeer,10) #impostare bene le dimensioni
				if not rispostaPeer:
					print "ERRORE RICEZIONE PACCHETTO DOWNLOAD DAL PEER"
					sys.exit(1)
				identificativoPeer=rispostaPeer[0:4]
				#print identificativoPeer
				if identificativoPeer !="ARET":
					print "ERRORE RISPOSTA DOWNLOAD PEER"
				nChunk=int(rispostaPeer[4:10])  
				#print nChunk
				
				conta=1	
				while conta <= nChunk:
					lenChunk=leggi(peer_socketPeer,5)					
					lenChunk=int(lenChunk)	
					#print lenChunk
					#lenChunk=risposta[0:5]
					#chunk=int(lenChunk)
					data=leggi(peer_socketPeer,lenChunk)						
					os.write(fd, data)	
					conta=conta+1
					#print "conta: ",conta
				print "Il file è stato salvato con successo!"
				
				os.close(fd)			
				peer_socketPeer.close()  #chiudo la socket con il peer da cui ho effettuato il download
			#..................................................................................
			if scelta== "5": #Logout
				#peer_socket=creazioneSocket(IPP2P,PortaP2P)
				peer_socket=creazioneSocket(IPP2P,"3000")   ##################################################
				print "logout....."
				logo(peer_socket,SessionID)
				scriviLog("Inviato LOGO"+SessionID)
				#risposta al logout
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
			
				#chiusura socket
				peer_socket.close()				
				ascolto.closeSocketACK()
				break
