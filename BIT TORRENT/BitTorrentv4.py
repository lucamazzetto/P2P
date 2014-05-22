#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#progetto3

#io  			fd00:0000:0000:0000:7ed1:c3ff:fe76:362a
#guerra 		fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
#mazzetto		fd00:0000:0000:0000:26fd:52ff:fe7a:6c5a

import socket,stat,sys,hashlib,os,threading,thread,time,re,shutil
from threading import *
from operator import itemgetter, attrgetter
from Tkinter import * 
from random import * 
import random
import string 
from math import *
from time import sleep
import tkFileDialog
script_dir = os.path.dirname(__file__)
mioIP="192.168.001.008"
miaPorta="50000"
ipTracker=""
portaTracker=""
sessionID=""
dimParte="262144"
lock=Lock()
lockThreadFiniti=Lock()
lockTd=Lock()

spegniMenu=0
fileCaricati=[] #lista sull' idFile dei file aggiunti al Tracker      {idFile: fileName,numParti}
fileTrovati=[] #file che tornano dal tracker dopo la ricerca  {indice numerico: randId,fileName,lenFile,lenParti}
listaScaricati=[]
td={} #array dei thread di download delle parti
threadFiniti=0
partiScaricate=[]

########CLASSI##########
class PB:

    # Crea progress bar e frame che lo contiene
    def __init__(self, width, height,fileName,numPezzi):
        self.root = Toplevel()
        self.root.resizable(False, False)
        self.root.title("Download di "+fileName)
        self.width = width
        self.height = height
        self.numPezzi= numPezzi
        self.contatore=1
        
        self.frameBar = Frame(self.root,relief='ridge', bd=3)
        #self.frameBar.pack(fill='both', expand=1)
        self.frameBar.grid(row=0, column=0, padx=10, pady=10,sticky="we")
        
        #self.frameInfo = LabelFrame(self.root,text="Parti Scaricate", width="250", height="50", bd="1", relief="ridge")
        self.frameInfo = LabelFrame(self.root,text="Parti Scaricate", bd="1", relief="ridge")
        self.frameInfo.grid(row=1, column=0, padx=10, pady=10,sticky="we")
        
        #~ self.__canvas = Tkinter.Canvas(self.__root, width=width, height=height)
        self.canvas = Canvas(self.frameBar, bg='white', width=width, height=height, highlightthickness=0, relief='flat', bd=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10,sticky="we")
        

        

        self.infoParti=Text(self.frameInfo, relief=SUNKEN, bd=2, setgrid=1,width=65, height=15,wrap='word',state=DISABLED)
        self.infoParti.grid(row=0, column=0,padx=5, pady=5)
        #self.info1.pack(side=LEFT, expand=Y, fill=BOTH,padx=5, pady=5)
        
        
        self.labelParti = Label( self.frameInfo, text="IP" )
        self.labelParti.grid(row=0, column=1, padx=5, pady=5,sticky="e")
		
        

    # Open Progress Bar
    def open(self):
        self.root.deiconify()

    # Close Progress Bar
    def close(self):
        self.root.withdraw()

    # Update Progress Bar
    def update(self,pezzo,ip):
        #self.__canvas.delete(Tkinter.ALL)
		print "numpezzi:",self.numPezzi 
		print "pezzo:",pezzo
		wpezzettino= self.width/self.numPezzi  
		print "wpezzettino:",wpezzettino
		
		iniziox=pezzo*wpezzettino
		print "iniziox:",iniziox
		finex=(pezzo+1)*wpezzettino
		print "finex:",finex
		#self.__canvas.create_rectangle(0+pezzo*wpezzettino, 0, wpezzettino,self.height, fill='blue'
		self.conta(self.numPezzi,pezzo,ip)
		#FUNZIONA self.__canvas.create_rectangle(iniziox, 0, finex,self.__height, fill='red',outline="")
		self.canvas.create_rectangle(iniziox, 0, finex,self.height, fill='blue',outline="")
		#...........................(iniziox,y,finex,finey)
		self.root.update()
		
    def conta(self,numpezzi,pezzo,ip):
		self.labelParti.configure(text=str(self.contatore)+"/"+str(int(numpezzi)))
		self.infoParti.config(state=NORMAL)
		self.infoParti.insert(END,"Scaricato pezzo "+str(pezzo)+" da "+ip+"\n")
		self.infoParti.config(state=DISABLED)
		self.infoParti.yview(END)
		self.contatore=self.contatore+1 

		
		
class SalvaFileTrovati:	
	def __init__(self,RANDID,FILENAME,LENFILE,LENPARTI):		
		self.RANDID=RANDID
		self.FILENAME=FILENAME
		self.LENFILE=LENFILE
		self.LENPARTI=LENPARTI
		self.LISTAOCCORRENZE=[]
		
		
class creaListaIpPorta:
	def __init__(self, IP, PORTA):
		self.IP=IP
		self.PORTA=PORTA


class creaListaOccorrenze:
	def __init__(self, numParte):
		self.NUMPARTE=numParte
		self.OCCORRENZE="0"
		self.LISTAIPPORTA=[]
		#l=creaListaIpPorta(IP, PORTA)
		#self.LISTAIPPORTA.append(l)



########FUNZIONI########
def aggiornaBarra(partNum,bar):
	lock.acquire()
	print "SONO QUI"
	try:
		bar.update(partNum)
		
	finally:
		lock.release
		
def aggiornaThreadFiniti(threadFiniti):
	lockThreadFiniti.acquire()
	print "sono in aggiornaThreadFiniti"
	try:
		threadFiniti=threadFiniti+1
	finally:
		lockThreadFiniti.release

def aggiornaTd(td,indice):
	lockTd.acquire()
	print "sono in aggiornaThreadFiniti"
	try:
		td.pop(indice)
	finally:
		lockTd.release
				
def creaMultipli8(num):
	resto=num % 8
	print resto
	if resto !=0:	
		num=num+(8-resto)		
	return num
	
def leggi(s,dim):
	dato=s.recv(dim)
	while len(dato)<dim:
		dato=dato+s.recv(1)
	#print dato
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
	


#aggiungo 0 davanti al numero se è troppo corto
def controllaArgomentoNumero(dim,argomento): 
	if len(argomento) < dim :
		differenza=dim-len(argomento)
		i=0
		while i<differenza:
			argomento="0"+argomento
			i=i+1
	return argomento
	
#LUNGO -> TRONCO, CORTO -> SPAZI	
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

def scriviLog(self,Str):
	logTime = time.localtime(time.time())
	ora=time.strftime("%d/%m/%Y %H:%M:%S", logTime)
	Str=Str+"\n"
	self.info1.insert(END,Str)
	self.info1.yview(END)



def creazioneSocket(IP,Porta):
	#apertura socket	
	peer_socket = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
	peer_socket.connect((IP,int(Porta)))
	return peer_socket	
	
def generaIdFile(N):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(N)) 
	
def esisteFile(percorsoFile):
	try:
		fd=open(percorsoFile,"rb")		
		return 1
	except:
		print "Il file non esiste"
		return 0
				
def fileSize(percorso):
	info = os.stat(percorso)
	size = info[stat.ST_SIZE]
	return size
	
#funzione che crea una cartella se non esiste
def creaCartella(cartella):
    percorso = os.path.dirname(cartella)
    if not os.path.exists(percorso):
        os.makedirs(percorso)
        
def creaFile(idFile,fileName):
	chunkfiles = []
	chunkfiles= os.listdir(script_dir+"/PartiTemp/"+idFile+"/")
	print "Lista parti da concatenare",os.listdir(script_dir+"/PartiTemp/"+idFile+"/")
	chunkfiles.sort(key=lambda x: [int(y) for y in x.split('.')])
	print "ordinati: ",chunkfiles
	destination = open("./fileScaricati/"+fileName, 'wb')
	for f in chunkfiles:
		shutil.copyfileobj(open(script_dir+"/PartiTemp/"+idFile+"/"+f, 'rb'), destination)
	destination.close()

#######FUNZIONI CREA PACCHETTI########
#login
def logi(IP,PORTA):	
	pacchetto="LOGI"+IP+PORTA
	return pacchetto

def logo(SessionID):
	pacchetto="LOGO"+SessionID
	return pacchetto
	
def addr(SessionID,idFile,lenFile,lenParti,Filename):
	Filename=controllaArgomentoStringa(100,Filename)
	pacchetto="ADDR"+SessionID+idFile+lenFile+lenParti+Filename
	return pacchetto
	
def look(SessionID,Ricerca):
	Ricerca=controllaArgomentoStringa(20,Ricerca)
	pacchetto="LOOK"+SessionID+Ricerca
	return pacchetto

def fchu(SessionID,idFile):
	pacchetto="FCHU"+SessionID+idFile
	return pacchetto
	
def retp(idFile,partNum):
	pacchetto="RETP"+idFile+str(partNum).rjust(8,"0")
	return pacchetto
	
def rpad(SessionID,idFile,partNum):
	pacchetto="RPAD"+SessionID+idFile+str(partNum).rjust(8,"0")
	return pacchetto


#########THREADS##########

class ThreadAscolto(threading.Thread):
	ip=""
	porta=""
	maxconn=5	
	socketACK=''
	acceso=1
	gestioneRisposte={}
	def __init__(self,Porta):
		threading.Thread.__init__(self)
		self.socketACK.setblocking(1)		
		self.porta=Porta		
	def run(self):
		# Create the socket
		try:
			self.socketACK=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.socketACK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socketACK.bind(("", int(self.porta)))
		except:
			print "Errore thread ascolto: Bind"
			return False

		# Listen on it
		try:
			self.socketACK.listen(self.maxconn)
		except:
			print "Errore thread ascolto: Listen"
			return False			

		while self.acceso:
			try:				
				(conn, addr) = self.socketACK.accept()
				cid=addr[0]			
				self.gestioneRisposte[cid]=ThreadRisposte(cid, conn)
				self.gestioneRisposte[cid].start()
			except:
				print "Errore thread ascolto: Accept"
				return False
					
	def closeSocketACK(self):
		try:
			self.acceso=0
			self.socketACK.close()
			return True
		except:
			print "Errore thread ascolto: Close"
			return False
			
			
class ThreadRisposte(threading.Thread): 

	id=''
	socketACK=None	
	receive=1
	server=None

	def __init__(self, id, socket):
		threading.Thread.__init__(self)
		self.id=id
		self.socketACK=socket
		

	def run(self):	
		global spegniMenu
		global fileCaricati
		global dimParte
		
		print "dentro threadRisposte"
		print self.id
		identificativo=leggi(self.socketACK,4)#146B per ogni riga
		if not identificativo:
			print "ERRORE RICEZIONE identificativo threadRisposte"
			sys.exit(1)					
		if identificativo !="RETP":
			print "ERRORE RISPOSTA IDENTIFICATIVO INIZIO THREAD ASCOLTO...",identificativo
			#scriviLog(self,"ERRORE RISPOSTA IDENTIFICATIVO INIZIO THREAD ASCOLTO..."+identificativo)
			self.socketACK.close()	
			
		randId=leggi(self.socketACK,16)
		partNum=int(leggi(self.socketACK,8))
		dimParte=int(dimParte)
		#~ listaScaricati=[]
		#~ listaScaricati=os.listdir("./fileScaricati/")
		operazione=2  
		for i in range(len(fileCaricati)):
			if randId in fileCaricati[i]:  #è un mio file devo spezzettarlo
				percorsoFile=script_dir+"/immagine/"+fileCaricati[i][1]
				print "percorso ",percorsoFile
				operazione=1
				break
			#~ else:   #è un file che ho scaricato e ho già le parti
				#~ percorsoFile="./PartiTemp/"+randId+"/"+str(partNum)
				#~ operazione=0
				#~ #break		
				
###################################################################
		for i in range(len(listaScaricati)):
			if randId in listaScaricati[i]:  #è un mio file devo spezzettarlo
				percorsoFile=script_dir+"/PartiTemp/"+randId+"/"+str(partNum)
				print "percorso ",percorsoFile
				operazione=0
				break
				
		if operazione==2:  #il file non è ancora stato scaricato completamente--> le parti scaricate si trovano in parti temp
			operazione=0
			percorsoFile=script_dir+"/PartiTemp/"+randId+"/"+str(partNum)
				
####################################################################			
	
				
		if operazione==1:
			#devo andare a leggere la parte giusta dal file
			fd = open(percorsoFile,"rb")
			print "read(1): ",fd.read(1)
			#print "rgomento seek=",(partNum)*int(dimParte))
			fd.seek(int(partNum)*int(dimParte))
			parte=fd.read(dimParte)
			
			
			nomeTemp=str(randint(0,10000))
			ftemp = open(script_dir+"/PartiTemp/"+nomeTemp, "wb")	
			ftemp.write(parte)
			ftemp.close()
			ftemp = open(script_dir+"/PartiTemp/"+nomeTemp,"rb")
			
			filesize = os.stat(script_dir+"/PartiTemp/"+nomeTemp).st_size	
			nChunk=filesize/4096    
			
			if (filesize%4096) !=0:  #se resto=0 allora i valori sono divisibili altrimenti aggiungiamo un valore
				nChunk=nChunk+1	
			nChunk=str(nChunk).zfill(6)
			print "nchunk: ",nChunk		
			pacchetto="AREP"+nChunk
			#print pacchetto
			print "Trasferimento in corso.."
			i=1
			while i<= int(nChunk):
				
				buf=ftemp.read(4096) #legge dal file				
				if not buf: break
				lBuf=len(buf)
				lBuf=str(lBuf).zfill(5)	
				pacchetto=pacchetto+lBuf+buf   #costruisco il pacchetto
				i=i+1	
			print "Trasferimento effettuato!!"			
			self.socketACK.send(pacchetto) 
			ftemp.close()
			time.sleep(50)		
			self.socketACK.close()	
			os.remove(script_dir+"/PartiTemp/"+nomeTemp)
		else:
			#ho la parte già disponibile
			fd = os.open(percorsoFile,os.O_RDONLY)		
			filesize = os.fstat(fd)[stat.ST_SIZE]		
			nChunk=filesize/4096    
			
			if (filesize%4096) !=0:  #se resto=0 allora i valori sono divisibili altrimenti aggiungiamo un valore
				nChunk=nChunk+1	
			nChunk=str(nChunk).zfill(6)
					
			pacchetto="AREP"+nChunk
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
	
class ThreadAfch(threading.Thread): 
	sessionID=''

	def __init__(self,sessionID, idFile, modo, numParti, indiceFile,selfGui, numPezzi):
		threading.Thread.__init__(self)
		self.modo=modo
		self.sessionID=sessionID
		self.idFile=idFile
		self.numParti=numParti #sono i BLOCCHI
		self.indiceFile=indiceFile
		self.selfGui=selfGui
		self.numPezzi=numPezzi #num parti
		print "numpezzi inizio thread ", numPezzi
		self.fineDownload=0

	def run(self):	
		global ipTracker
		global portaTracker
		global fileTrovati
		pacchetto=fchu(self.sessionID,self.idFile)
		print "pacchetto",pacchetto
		if self.modo=="Ricerca":
			try:
				socket=creazioneSocket(ipTracker,portaTracker)
				socket.send(pacchetto)									#invio FCHU+SessionId+RandomId
				print "inviato"
				scriviLog(self.selfGui,"Inviato "+pacchetto)
			except:
				print "Errore invio pacchetto FCHU"
			identificativo=leggi(socket,4)#146B per ogni riga			leggo AFCH
			if not identificativo:
				print "ERRORE RICEZIONE identificativo AFCH"
				sys.exit(1)					
		
			self.numPezzi=creaMultipli8(int(self.numPezzi))
			
			#inizializzo la listaoccorrenze
			for i in range(0,int(self.numPezzi)):				
				fileTrovati[self.indiceFile].LISTAOCCORRENZE.append(creaListaOccorrenze(i))
				
			print "numPezzi= ",self.numPezzi	
			print "LISTA OCCORRENZE INIZIALIZZATA"
			for i in range(0,int(self.numPezzi)):
				print "i",i,")",fileTrovati[self.indiceFile].LISTAOCCORRENZE[i].NUMPARTE,fileTrovati[self.indiceFile].LISTAOCCORRENZE[i].OCCORRENZE
				
			
			numPeer=leggi(socket,3)
			
			#scorro tutti i peer che hanno almeno una parte del file
			for indicePeer in range(int(numPeer)):
				#per ogni peer leggo ip porta part list
				ipPeer=leggi(socket,39)
				portaPeer=leggi(socket,5)
				partList=leggi(socket,self.numParti)
				print "numParti cioè blocchi ",self.numParti
				newPartList=""
				#trasformo in binario il numParti
				for byte in range(len(partList)):
					temp=ord(partList[byte]) #ho un intero
					temp = bin(temp)[2:].rjust(8, '0')
					newPartList=newPartList+temp
				print "newPartList",newPartList
				#scorro tutti gli zeri e uni
				for blocco in range(0,self.numParti):
					print "sono nel for-->blocco=",blocco
					for bit in range(0,8):
						
						##########quiiiiiiiiii########
						x=bit+8*blocco
						print "x=",x
						if newPartList[x]=="1" :
							print "la partlist ha bit=1"
							#print "indiceFile",self.indiceFile
							 #print "filename ",fileTrovati[self.indiceFile].FILENAME
							indice=((7+8*blocco)-x)+8*blocco
							print "occorrenza ",fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].OCCORRENZE
							fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].OCCORRENZE=int(fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].OCCORRENZE) +1
							fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].LISTAIPPORTA.append(creaListaIpPorta(ipPeer, portaPeer))
							print "occorrenza +1 ",fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].OCCORRENZE
			print "LISTA OCCORRENZE"
			for i in range(0,int(self.numPezzi)):
				print "i",i,")",fileTrovati[self.indiceFile].LISTAOCCORRENZE[i].NUMPARTE, fileTrovati[self.indiceFile].LISTAOCCORRENZE[i].OCCORRENZE
			#chiudo socket e la riapro all'inizio del while
			socket.close()
				
		else:
			while self.fineDownload==0:
				try:
					socket=creazioneSocket(ipTracker,portaTracker)
					socket.send(pacchetto)
					#scriviLog(self.selfGui,"Inviato "+pacchetto)
				except:
					print "Errore invio pacchetto FCHU 2"
				identificativo=leggi(socket,4)#146B per ogni riga
				if not identificativo:
					print "ERRORE RICEZIONE identificativo AFCH"
					sys.exit(1)	
				
				print "self.numpezzi ", self.numPezzi
				self.numPezzi=creaMultipli8(int(self.numPezzi))				
				print "Risultato self.numpezzi ", self.numPezzi
				#inizializzo la listaoccorrenze
				fileTrovati[self.indiceFile].LISTAOCCORRENZE=[]
				for i in range(0,int(self.numPezzi)):
					fileTrovati[self.indiceFile].LISTAOCCORRENZE.append(creaListaOccorrenze(i))
				
				numPeer=leggi(socket,3)
				
				#scorro tutti i peer che hanno almeno una parte del file
				for indicePeer in range(int(numPeer)):
					#per ogni peer leggo ip porta part list
					ipPeer=leggi(socket,15)
					portaPeer=leggi(socket,5)
					partList=leggi(socket,self.numParti)
					
					newPartList=""
					#trasformo in binario il numParti
					for byte in range(len(partList)):
						temp=ord(partList[byte]) #ho un intero
						temp = bin(temp)[2:].rjust(8, '0')
						newPartList=newPartList+temp
				
					#scorro tutti gli zeri e uni
					for blocco in range(0,self.numParti):
						for bit in range(0,8):
						
							x=bit+8*blocco
							
							if newPartList[x]=="1" :
									indice=((7+8*blocco)-x)+8*blocco
									fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].OCCORRENZE=int(fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].OCCORRENZE) +1
									fileTrovati[self.indiceFile].LISTAOCCORRENZE[indice].LISTAIPPORTA.append(creaListaIpPorta(ipPeer, portaPeer))
				#~ print "LISTA OCCORRENZE NEL DOWNLOAD"
				#~ for i in range(0,int(self.numPezzi)):
					#~ print "i",i,")",fileTrovati[self.indiceFile].LISTAOCCORRENZE[i].NUMPARTE, fileTrovati[self.indiceFile].LISTAOCCORRENZE[i].OCCORRENZE
				#chiudo socket e la riapro all'inizio del while
				socket.close()
	
				sleep(60)
			
	#da chiamare quando il download finisci per interrompere l'aggiornamento		
	def stopAggiornamento(self):
		self.fineDownload=1	
				
		
#Thread Download. Crearne uno per ogni RETP
class ThreadDownload(threading.Thread): 

	def __init__(self, idFile, partNum, ip, porta,sessionID,indiceThread,bar,selfGui):
		threading.Thread.__init__(self)
		self.idFile=idFile
		self.partNum=partNum
		self.ip=ip
		self.porta=porta
		self.sessionID=sessionID
		self.indiceThread=indiceThread
		self.bar=bar
		self.selfGui=selfGui

	#devo inviare RETP, ricevere AREP e avvisare il Tracker inviando RPAD e ricevendo APAD
	def run(self):	
		#~ global ipTracker
		#~ global portaTracker
		global td
		
		
		#threadFiniti=threadFiniti+1
		print "Sono dentro al Thread self.indiceThread: ",self.indiceThread
		 
		#scriviLog(self.selfGui,"Partnum: "+str(self.partNum))

		try:
			pacchetto=retp(self.idFile,self.partNum)
			print "pacchetto RETP",pacchetto
		except:
			print "errore creazione pacchetto"
		
		try:
			print "Avvio socket con ip,porta ",self.ip,self.porta
			s=creazioneSocket(self.ip,self.porta)
			
			s.send(pacchetto)
			print "pacchetto RETP inviato"
			s.shutdown(1)
			#scriviLog(self.selfGui,"INVIATO: "+pacchetto)
		except:	
			print "Errore socket RETP...riprovo"
			try:
				print "Avvio socket con ip,porta ",self.ip,self.porta
				s=creazioneSocket(self.ip,self.porta)
				
				s.send(pacchetto)
				print "pacchetto RETP inviato secondo tentativo"
				s.shutdown(1)
				#scriviLog(self.selfGui,"INVIATO: "+pacchetto)
			except:	
				print "Errore socket RETP seconda volta"
			#scriviLog(self.selfGui,"ERRORE INVIO: "+pacchetto)
		#devo ricevere AREP
		
		identificativo=leggi(s,4)#146B per ogni riga
		print "Leggo identificativo ",identificativo
		if (not identificativo) or (identificativo!="AREP") :
			print "ERRORE RICEZIONE identificativo AREP"
			#scriviLog(self.selfGui,"ERRORE RICEZIONE identificativo AREP")
			sys.exit(1)	

		loc=script_dir+"/PartiTemp/"+self.idFile+"/"
		creaCartella(loc)
		fd = os.open(loc+str(self.partNum), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0666)			

		numChunk=int(leggi(s,6))	
		conta=1	
		#print " fuori while conta, nchunck",conta,numChunk
		while conta <= numChunk:
			#print " dentro while conta, nchunck",conta,numChunk
			lenChunk=leggi(s,5)					
			lenChunk=int(lenChunk)	
			
			data=leggi(s,lenChunk)					
			os.write(fd, data)	
			conta=conta+1			
		
		print "Il file è stato salvato con successo!"
		os.close(fd)			
		s.close() 
		print "td prima: ",td
		td.pop(self.indiceThread)
		print "td dopo ",td
		
		#aggiorno la barra
		#aggiornaBarra(self.partNum,self.bar)
		#self.bar.update(self.partNum)
		
		#DEVO SEGNARMI CHE HO SCARICATO QUESTA PARTE (lo facciamo nel main)
		
		#DEVO AVVISARE IL TRACKER
		pacchetto=rpad(self.sessionID,self.idFile,self.partNum) #####CONTROLLA DIMENSIONE PARTNUM!!!!
		try:
			s=creazioneSocket(ipTracker,portaTracker)
			s.send(pacchetto)
			#s.shutdown(1)
			#scriviLog(self.selfGui,"INVIATO: "+pacchetto)
		except:	
			print "Errore socket RPAD"
			#scriviLog(self.selfGui,"ERRORE INVIO: "+pacchetto)
		#devo ricevere APAD
		identificativo=leggi(s,4)#146B per ogni riga
		if (not identificativo) or (identificativo!="APAD") :
			print "ERRORE RICEZIONE identificativo APAD"
			#scriviLog(self.selfGui,"ERRORE RICEZIONE identificativo APAD")
			sys.exit(1)
		
		numPartiTot= leggi(s,8)
		#scriviLog(self.selfGui,"Scaricata parte "+str(self.partNum)+" -> parti totali: "+numPartiTot)
		s.close()	
		
		#AVVISO ME STESSO CHE HO SCARICATO UNA PARTE PER FARNE AVVIARE UN'ALTRA
		#cioè tolgo il thread dall'array td
		
		#incremento il numero dei threadfiniti cioè il numero di parti realmente scaricate
		#aggiornaThreadFiniti(threadFiniti)
		



class MiaApp:
	def __init__(self, finestra):
	  
		self.tAscolto=""
		
		self.finestra = finestra
		
		
		finestra.title("bitTorrent")                  
		#finestra.geometry("%dx%d+%d+%d" % (600, 300, 0, 0))
		finestra.resizable(False, False)

		self.frame1 = LabelFrame(self.finestra,text="Dati Login Tracker", width="250", height="150", bd="1", relief="ridge")
		self.frame2 = LabelFrame(self.finestra,text="Aggiunta File", width="250", height="35", bd="1", relief="ridge")
		self.frame3 = LabelFrame(self.finestra,text="Ricerca File", width="250", height="35", bd="1", relief="ridge")
		self.frame4 = LabelFrame(self.finestra,text="Download File", width="250", height="35", bd="1", relief="ridge")
		self.frame5 = LabelFrame(self.finestra,text="Info", width="250", height="100", bd="1", relief="ridge")
		self.frame6 = LabelFrame(self.finestra,text="Tuoi dati", width="250", height="50", bd="1", relief="ridge")
		

		self.frame1.grid_propagate(0)
		#self.frame2.grid_propagate(0)


		self.frame1.grid(row=0, column=0, padx=10, pady=2, sticky="wesn",rowspan=3)
		self.frame2.grid(row=0, column=1, padx=10, pady=2,sticky="wesn")
		self.frame3.grid(row=1, column=1, padx=10, pady=2,sticky="wesn")
		self.frame4.grid(row=2, column=1, padx=10, pady=2,sticky="wesn")
		self.frame5.grid(row=3, column=0, padx=10, pady=10, columnspan=2,sticky="we")
		self.frame6.grid(row=4, column=0, padx=10, pady=10, columnspan=2,sticky="we")


		#frame login
		self.label1 = Label( self.frame1, text="IP" )
		self.label1.grid(row=0, column=0, padx=5, pady=5)
		self.entry1 = Entry(self.frame1, relief=SUNKEN, border=2, width=20)
		self.entry1.grid(row=0, column=1, padx=5, pady=5)
		self.label2 = Label( self.frame1, text="PORTA" );
		self.label2.grid(row=1, column=0, padx=5, pady=5)
		self.entry2 = Entry(self.frame1, relief=SUNKEN, border=2, width=20 )
		self.entry2.grid(row=1, column=1, padx=5, pady=5)
		self.bottone1 = Button(self.frame1, text="Login", width="7", command=self.click_bottone1)
		self.bottone1.grid(row=2, column=0, columnspan=2)
		self.bottone2 = Button(self.frame1, text="Logout",width="7",state='disabled', command=self.click_bottone2)
		self.bottone2.grid(row=3, column=0, columnspan=2)

		#frame aggiunta file
		self.entry3 = Entry(self.frame2, relief=SUNKEN, border=2, width=20 );
		self.entry3.grid(row=0, column=0, padx=5, pady=5)
		self.bottone3 = Button(self.frame2, text="Aggiungi", width="7", command=self.click_bottone3)
		self.bottone3.grid(row=0, column=1,padx=5, pady=5)

		#frame ricerca
		self.entry4 = Entry(self.frame3, relief=SUNKEN, border=2, width=20);
		self.entry4.grid(row=0, column=0, padx=5, pady=5)
		self.bottone4 = Button(self.frame3, text="Cerca", width="7", command=self.click_bottone4)
		self.bottone4.grid(row=0, column=1,padx=5, pady=5)

		#frame download
		self.entry5 = Entry(self.frame4, relief=SUNKEN, border=2, width=20 );
		self.entry5.grid(row=0, column=0, padx=5, pady=5)
		self.label4 = Label( self.frame4, text="Pt:" );
		self.label4.grid(row=0, column=1, padx=5, pady=5)
		self.entry8 = Entry(self.frame4, relief=SUNKEN, border=2, width=3 );
		self.entry8.grid(row=0, column=2, padx=5, pady=5)
		self.bottone5 = Button(self.frame4, text="Download", width="7",command=self.click_bottone5)
		self.bottone5.grid(row=0, column=3,padx=5, pady=5)
		
		
		#frame info
		self.info1=Text(self.frame5, relief=SUNKEN, bd=2, setgrid=1, height=20,wrap='word');
		#self.info1.grid(row=0, column=0,padx=5, pady=5, expand=X)
		self.info1.pack(side=LEFT, expand=Y, fill=BOTH,padx=5, pady=5)
		#self.bar1=Scrollbar(self.frame5);
		#self.bar1.pack(side=LEFT, fill=Y)
		#self.info1['yscrollcommand']=self.bar1.set; 
		#self.bar1['command']=self.info1.yview

		#frame tuoi dati
		
		self.label3 = Label( self.frame6, text="Mio IP:" );
		self.label3.grid(row=0, column=0, padx=5, pady=5)
		sip = StringVar()
		self.entry6 = Entry(self.frame6,textvariable=sip, relief=SUNKEN, border=2, width=20,state='readonly')
		self.entry6.grid(row=0, column=1, padx=15, pady=10)
		sip.set(mioIP)	
		
		self.label4 = Label( self.frame6, text="Mia Porta:" );
		self.label4.grid(row=0, column=2, padx=5, pady=5)
		sporta = StringVar()
		self.entry7 = Entry(self.frame6, textvariable=sporta,relief=SUNKEN, border=2, width=10,state='readonly')
		self.entry7.grid(row=0, column=3, padx=15, pady=10)
		sporta.set(miaPorta)
		
		self.bottone6 = Button(self.frame6, text="Cambia", width="7",command=self.click_bottone6)
		self.bottone6.grid(row=0, column=4,padx=20, pady=5)
		
	
	# BOTTONE LOGIN -------------------------------------------------------------------------------------------
	def click_bottone1(self):
		global mioIp
		global miaPorta
		global ipTracker
		global portaTracker
		global sessionID
		
		ipTracker=self.entry1.get()
		portaTracker=self.entry2.get()
		if (ipTracker != '') and (portaTracker != '') :
			self.info1.insert(INSERT,"Inseriti "+ipTracker+":"+portaTracker+"\n" )
			self.entry1.configure(state='disabled')
			self.entry2.configure(state='disabled')
			self.bottone1.configure(state='disabled')
			self.bottone2.configure(state=NORMAL)
			ipTracker=creaIP(ipTracker)
			print ipTracker
			portaTracker=controllaArgomentoNumero(5,portaTracker)
			print portaTracker
			#invio LOGI
			try:
				s=creazioneSocket(ipTracker,portaTracker)
				scriviLog(self,"OK connesso")
				pacchetto= logi(mioIP,miaPorta)
				scriviLog(self,"OK connesso")
				s.send(pacchetto)
				scriviLog(self,"Inviato LOGI:  "+pacchetto)
			except:
				scriviLog(self,"Errore Invio pacchetto LOGI")
				#print "Errore Invio pacchetto LOGI"
			
			#ricevo ALGI			
			risposta=leggi(s,20) 
			if not risposta:
				#print "ERRORE RICEZIONE PACCHETTO ALGI: nessuna risposta"
				scriviLog(self,"ERRORE RICEZIONE PACCHETTO ALGI: nessuna risposta")
				sys.exit(1)
			identificativo=risposta[0:4]
			if identificativo !="ALGI":
				#print "ERRORE IDENTIFICATIVO: no ALGI"
				scriviLog(self,"ERRORE IDENTIFICATIVO: no ALGI")
				sys.exit(1)
			sessionID=risposta[4:len(risposta)]
			#se sono gia loggato
			if sessionID=="0000000000000000":
				#print "SessionID già presente"
				scriviLog(self,"SessionID già presente")
				#sys.exit(1)
				##########SESSIONID######
				sessionID="EM3M3OSBOGT1OP4I"
			#print "SEI LOGGATO A: ",ipTracker," ",portaTracker
			scriviLog(self,"SEI LOGGATO A: "+ipTracker+" "+portaTracker)
			s.close()
			
			self.tAscolto=ThreadAscolto(miaPorta)
			self.tAscolto.start()
				
		else:
			self.info1.insert(INSERT,"Inserisci IP e PORTA !!!\n" )
			
			
	# BOTTONE LOGOUT------------------------------------------------------------------------------------------
	def click_bottone2(self):
		global mioIp
		global miaPorta
		global ipTracker
		global portaTracker
		global sessionID
		
		#invio LOGO
		try:
			s=creazioneSocket(ipTracker,portaTracker)
			pacchetto= logo(sessionID)
			s.send(pacchetto)
			scriviLog(self,"Inviato LOGO:  "+pacchetto )
		except:
			scriviLog(self,"Errore Invio pacchetto LOGO")
			print "Errore Invio pacchetto LOGO"

		
		#LOGOUT
		identificativo=leggi(s,4)#146B per ogni riga
		
		if identificativo =="NLOG":		
			partDown=leggi(s,10)
			print "Non puoi effettuare il Logout"
			print "PartDown = ",partDown
			scriviLog(self,"Non puoi effettuare il Logout. PartDown = "+partDown)
		
		if identificativo =="ALOG":				
			partOwn=leggi(s,10)
			print "Logout effettuato"
			print "PartOwn = ",partOwn
			scriviLog(self,"Logout effettuato. PartOwn = "+partOwn)
			self.tAscolto.closeSocketACK()	
			self.entry1.configure(state=NORMAL)
			self.entry2.configure(state=NORMAL)
			self.bottone1.configure(state=NORMAL)	
			self.bottone2.configure(state='disabled')	

		s.close()
		
	
	# BOTTONE AGGIUNGI ------------------------------------------------------------------------------------------
	def click_bottone3(self):
		global mioIp
		global miaPorta
		global ipTracker
		global portaTracker
		global sessionID
		global dimParte
		
		percorsoFilename = tkFileDialog.askopenfilename(initialdir=script_dir+"/immagine/")
		
		
		if percorsoFilename!="":
			filename =percorsoFilename.split(os.sep)[-1]
		
			self.entry3.delete(0,END) 
			self.entry3.insert(0,filename)
			
			
			idFile=generaIdFile(16)
			s=creazioneSocket(ipTracker,portaTracker)
			print "Aggiunta file in corso....."
			print "ip porta tracker:", ipTracker, portaTracker
			dimFile=fileSize(percorsoFilename)
			dimFile=str(dimFile).zfill(10)
			#dimFile=controllaArgomentoNumero(10,dimFile)
			print "DimFile:", dimFile
			pacchetto=addr(sessionID,idFile,dimFile,str(dimParte),filename) 
			print "pacchetto", pacchetto
			s.send(pacchetto)
			scriviLog(self,"INVIATO - "+pacchetto)
			print"AGGIUNTO pacchetto:",pacchetto			
			
			identificativo=leggi(s,4)#146B per ogni riga
			if identificativo !="AADR":
				print "ERRORE IDENTIFICATIVO: no AADR"
				scriviLog(self,"ERRORE IDENTIFICATIVO: no AADR")
				sys.exit(1)				
				
			numPartiLetto=leggi(s,8)
			scriviLog(self,"RICEVUTO - "+identificativo+numPartiLetto)
			fileCaricati.append([idFile,filename,numPartiLetto])
			s.close()
			print fileCaricati
			#~ except:
				#~ 
				#~ print "Errore in Aggiunta file"
				#~ scriviLog(self,"Errore in Aggiunta file")
		else:
			scriviLog(self,"File non scelto")
			
	
	# BOTTONE CERCA ------------------------------------------------------------------------------------------
	def click_bottone4(self):
		global mioIp
		global miaPorta
		global ipTracker
		global portaTracker
		global sessionID
		global fileTrovati
		fileTrovati=[]
		ricerca=self.entry4.get()
		pacchetto=look(sessionID,ricerca)	
		try:
			s=creazioneSocket(ipTracker,portaTracker)
			s.send(pacchetto)
			print "Attendi risultati..."
			scriviLog(self,"INVIATO:"+pacchetto)
		except:
			print "Errore Socket invio pacchetto ricerca"
			scriviLog(self,"ERRORE INVIO:"+pacchetto)
			
		identificativo=leggi(s,4)#146B per ogni riga
		if identificativo !="ALOO":
			print "ERRORE IDENTIFICATIVO: no ALOO"
			scriviLog(self,"ERRORE IDENTIFICATIVO: no ALOO")
			sys.exit(1)	
		
		numIdRand=leggi(s,3)
		
		r=int(numIdRand)
		for i in range(0,r):
			#print "i",i
			idFile=leggi(s,16)
			fileName=leggi(s,100)
			lenFile=leggi(s,10)
			lenParti=leggi(s,6)
			fileTrovati.append(SalvaFileTrovati(idFile,fileName,lenFile,lenParti))
		
		scriviLog(self, "FILE TROVATI")
		for i in range(len(fileTrovati)):
			numPezzi=int(ceil(int(fileTrovati[i].LENFILE)/float(fileTrovati[i].LENPARTI)))
			scriviLog(self, str(i)+") "+fileTrovati[i].RANDID+" - "+fileTrovati[i].FILENAME+" LenFile:"+fileTrovati[i].LENFILE+" LenParti:"+fileTrovati[i].LENPARTI+" Numero Pezzi: "+str(numPezzi))
			print i,") ",fileTrovati[i].RANDID," - ",fileTrovati[i].FILENAME, " LenFile:",fileTrovati[i].LENFILE," LenParti:",fileTrovati[i].LENPARTI
		
		
		#chiudo la socket e la riapro nel thread per fchu-afch
		s.close() 
		
		for i in range(len(fileTrovati)):
			#calcolo num parti
			print "i",i
			numPezzi=int(ceil(int(fileTrovati[i].LENFILE)/float(fileTrovati[i].LENPARTI)))
			numParti=int(ceil((int(fileTrovati[i].LENFILE)/float(fileTrovati[i].LENPARTI))/8))
			#per ogni file trovato chiamo il thread per avere un suo stato iniziale delle parti
			t=ThreadAfch(sessionID, fileTrovati[i].RANDID, "Ricerca", numParti, i,self,numPezzi)
			t.start()
		
	# BOTTONE DOWNLOAD ------------------------------------------------------------------------------------------
	def click_bottone5(self):
		global mioIp
		global miaPorta
		global threadFiniti
		global fileTrovati
		global sessionID
		global td
		global partiScaricate
		global listaScaricati
		
		iFile=int(self.entry5.get())
		partiCont=int(self.entry8.get())
		indiceThread=0
		threadFiniti=0
		
		#numParti=numero dei byte nella partlist
		numParti=int(ceil((int(fileTrovati[iFile].LENFILE)/int(fileTrovati[iFile].LENPARTI))/8.0))
		numPezzi=int(ceil(int(fileTrovati[iFile].LENFILE)/float(fileTrovati[iFile].LENPARTI)))
		#print "numpezzi ", numPezzi
		#avvio l'aggiornamento della tabella del file voluto
		t=ThreadAfch(sessionID, fileTrovati[iFile].RANDID, "Download", numParti, iFile,self,numPezzi)
		t.start()
		
		
		
		#bar = PB(lunghezza,larghezza, titolo, numPezzi)
		print "creo la barra: numpezzi: ",numPezzi
		bar = PB(600, 25, fileTrovati[iFile].FILENAME,numPezzi)
		#apro la barra
		bar.open()
		#print "Threadfiniti , numPezzi", threadFiniti,numPezzi
		#td={}
		tFiniti=0
		while 1:
			if tFiniti<numPezzi:
				#print "ThreadFiniti<",tFiniti,"< numPezzi: ",numPezzi
				l=fileTrovati[iFile].LISTAOCCORRENZE
				occOrd=sorted(l, key=attrgetter('OCCORRENZE'))
				#print "primo if-->Numero thread attivi--> len(td): ",len(td)				
				if len(td)<partiCont:
					for i in range(0,len(occOrd)): #se non ci sono devo crearne, scorro la lista occord
						#print "for-->i: ",i
						#print "secondo if-->Numero thread attivi--> len(td): ",len(td)		
						if len(td)<partiCont: #controllo che non ci siano gia partiCont threads attivi							
							#controllo che la parte con occorrenza minore non sia gia in download/ o scaricata
							#print "len(occOrd):",len(occOrd)
							if occOrd[i].OCCORRENZE != "0":
								
								if occOrd[i].NUMPARTE not in partiScaricate: #se non c'è da 1 e la scarico
									
									indiceScelto=randint(0,len(occOrd[i].LISTAIPPORTA)-1)
									#print "indice scelto:", indiceScelto 
									ipScelto=occOrd[i].LISTAIPPORTA[indiceScelto].IP
									portaScelta=occOrd[i].LISTAIPPORTA[indiceScelto].PORTA							
									print "ip:", ipScelto,"porta:", portaScelta,"ip:", occOrd[i].NUMPARTE 
									td[indiceThread]=ThreadDownload(fileTrovati[iFile].RANDID,occOrd[i].NUMPARTE,ipScelto,portaScelta,sessionID,indiceThread,bar,self)
									td[indiceThread].start()
									#td[indiceThread].join()
									tFiniti=tFiniti+1
									#print "tFiniti: ",tFiniti
									#QUIIIIIIIIIIIIIII
									#raw_input("premi")
									sleep(0.1)
									bar.update(occOrd[i].NUMPARTE,ipScelto)
									partiScaricate.append(occOrd[i].NUMPARTE)
									indiceThread=indiceThread+1
							if len(td)==partiCont:
								break
			else:
				#print "ThreadFiniti>=numPezzi: "
				#td={}
				partiScaricate=[]
				break
			#sleep(0.5)
		t.stopAggiornamento()
					
		
		#se il numero delle parti scaricate è diverso dal numero totale di parti del file -> avvio thread				
		#~ while threadFiniti < numPezzi:
			#~ 
			#~ print "Threadfiniti", threadFiniti
			#~ print "NumPezzi ",numPezzi
					#~ 
			#~ l=fileTrovati[iFile].LISTAOCCORRENZE
			#~ occOrd=sorted(l, key=attrgetter('OCCORRENZE'))
			#~ 
			#~ print "len(td), partiCont",len(td),partiCont
			#~ if len(td)<partiCont: #controllo che non ci siano gia partiCont threads attivi
				#~ for i in range(0,len(occOrd)): #se non ci sono devo crearne, scorro la lista occord
					#~ #controllo che la parte con occorrenza minore non sia gia in download/ o scaricata
					#~ print "len(occOrd):",len(occOrd)
					#~ if occOrd[i].OCCORRENZE != "0":
						#~ if occOrd[i].NUMPARTE not in partiScaricate: #se non c'è da 1 e la scarico
							#~ 
							#~ indiceScelto=randint(0,len(occOrd[i].LISTAIPPORTA)-1)
							#~ print "indice scelto:", indiceScelto 
							#~ ipScelto=occOrd[i].LISTAIPPORTA[indiceScelto].IP
							#~ portaScelta=occOrd[i].LISTAIPPORTA[indiceScelto].PORTA							
						#~ 
							#~ td[indiceThread]=ThreadDownload(fileTrovati[iFile].RANDID,occOrd[i].NUMPARTE,ipScelto,portaScelta,sessionID,indiceThread,bar,self)
							#~ td[indiceThread].start()
							#~ #QUIIIIIIIIIIIIIII
							#~ #raw_input("premi")
							#~ sleep(0.1)
							#~ bar.update(occOrd[i].NUMPARTE)
							#~ partiScaricate.append(occOrd[i].NUMPARTE)
							#~ indiceThread=indiceThread+1
					#~ if len(td)==partiCont:
						#~ break
		#~ t.stopAggiornamento()
		scriviLog(self,"File in stato di creazione")
		while len(td)!=0:	
			sleep(0.1)					
		#ora ho tutte le parti e devo unirle
		creaFile(fileTrovati[iFile].RANDID,fileTrovati[iFile].FILENAME)
		
		
		print "File ",fileTrovati[iFile].FILENAME," scaricato."
		scriviLog(self,"File "+fileTrovati[iFile].FILENAME+" scaricato.")
		listaScaricati.append([fileTrovati[iFile].RANDID,fileTrovati[iFile].FILENAME])
		
	
	# BOTTONE CAMBIA INFO ------------------------------------------------------------------------------------------
	def click_bottone6(self):
		global mioIp
		global miaPorta

		if self.bottone6["text"]=="Cambia":
			self.bottone6.configure(text="OK")
			self.entry6.configure(state=NORMAL)
			self.entry7.configure(state=NORMAL)
			self.entry6.delete(0, END)
			self.entry7.delete(0, END)
		elif self.bottone6["text"]=="OK":
			self.bottone6.configure(text="Cambia")
			mioIP=creaIP(self.entry6.get())
			miaPorta=controllaArgomentoNumero(5,self.entry7.get())
			
			self.entry6.delete(0, END)
			self.entry6.insert(0, mioIP)
			self.entry7.delete(0, END)
			self.entry7.insert(0, miaPorta)
		
			self.entry6.configure(state="readonly")
			self.entry7.configure(state="readonly")
			
			
			
finestra = Tk()
miaApp = MiaApp(finestra)
finestra.mainloop()

