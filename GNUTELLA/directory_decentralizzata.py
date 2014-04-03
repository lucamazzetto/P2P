# -*- coding: utf-8 -*-

from socket import *
import thread as t
import sys
import re
import string
import random
#import structpktId
import structs as st
import hashlib
import os
import time
#import timeout

global ipr
global tpr

MY_IP="fd00:0000:0000:0000:7ed1:c3ff:fe76:362a" #"%03d.%03d.%03d.%03d" %(192,168,1,113)
MY_PORTS="05000" #"%05d" %(5080)
#MY_PORTC="%05d" %(5081)

#=====================================================================
#	PORTARLI IN VETTORE listaNeigh
#~ IP_PEER=["%03d.%03d.%03d.%03d" %(192,168,1,105),
		#~ "%03d.%03d.%03d.%03d" %(192,168,1,106),
		#~ "%03d.%03d.%03d.%03d" %(192,168,1,107)]
		#~ 
#~ PORT_PEER=["%05d" %(5080),"%05d" %(5080),"%05d" %(5080)]
#======================================================================
#IP_PEER1"%03d.%03d.%03d.%03d" %(192,168,1,105)
#IP_PEER2="%03d.%03d.%03d.%03d" %(192,168,1,106)
#IP_PEER3="%03d.%03d.%03d.%03d" %(192,168,1,107)
#PORT_PEER1="%05d" %(5080)
#PORT_PEER2="%05d" %(5080)
#PORT_PEER3="%05d" %(5080)
#NUM_PEER=3

# Timeout in millisec (300s)
TIMEOUT = 300000

# Num massimo di vicini da salvare
maxNeigh = 4
# Lista ip e porta vicini
listaNeigh = []
listaPort = []
# lock lista vicini
lockListaNeigh = t.allocate_lock()

# lista risultati ricerca con lock
listaRis=[]
lockListRis = t.allocate_lock()

# id pacchetto e tempo di invio del pacchetto di ricerca con lock
attesaRisp = ""
tempoAttesaRisp = 0
lockAttesaRisp = t.allocate_lock()

#pacchetto id e tempo invio del pacchetto di ricerca vicini con lock
attesaVicini = ""
tempoAttesaVicini = 0
lockAttesaVicini = t.allocate_lock()

#lista pacchetti gestiti dal server con lock
pktRic = []
lockPktRic = t.allocate_lock()

#path cartella condivisa
path = "/immagine"

#lunghezza chunck
lenchunk = 5000


# thread server in ascolto -----------------------------------------------------------------------
def handler_conn(s, ip ,p):
	cmd = s.recv(4)
	#print "cmd: "+cmd
	opts[cmd](s,ip,p)
	

def handler_listener():
	# Creazione della socket di tipo server in ascolto per captare messaggi dai peer nella rete
	try:
		s_sock = socket(AF_INET6, SOCK_STREAM)
		s_sock.bind(("",int(MY_PORTS)))

		s_sock.listen(10)
		while 1:
			c_sock, address = s_sock.accept()
			#print "\nConnessione da: ", address
			t.start_new_thread(handler_conn, (c_sock,address[0],address[1]))
	except error, msg:
		s_sock = None
		print "ERROR: " , msg
# ------------------------------------------------------------------------------------------------




#controllo pacchetti cicla sul vettore pacchetti gestiti, se già gestito ritorna 1
#mentre scorre cancella pacchetti fuori timeout (forse meglio farlo in altro thread)
def control_packet(pktId):
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	trovato = 0
	j = 0
	lockPktRic.acquire()
	now = time.time()
	while j < len(pktRic):
		#cancellazione pacchetto fuori timeout
		if (now - pktRic[j].timeCreaz > TIMEOUT):
			pktRic.pop(j)
		else:
			#se pacchetto già gestito
			if (pktRic[j].pktId == pktId):
				trovato = 1
			j = j + 1
	lockPktRic.release()
	return trovato




# ---------------------------------------------------------------------				
# funzioni "server"
#
# funzione ricerca
def quers(s, ip, p):
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	pktId = s.recv(16)
	ipr = s.recv(39)
	pr = int(s.recv(5))
	ttl = int(s.recv(2))
	ttl_send = "%02d" % ttl
	search_str = s.recv(20)
	ss = searc_str.strip()
	
	#controllo pacchetto
	if (control_packet(pktId) == 0):
		lockPktRic.acquire()
		now = time.time()
		pktRic.append(st.structPktId(pktId, now))
		dirs = []
		dirs = os.listdir(path)
		m = hashlib.md5()
		for files in dirs:
			#controllo esistenza file e invio pacchetti risposta
			if (files.lower().count(search_str.lower()) > 0):
				data = open(path+"/"+files,'rb').read()
				m.update(data)
				Filemd5 = "%16s" % m.digest()
				nomeFile = "%100s" % files
				risp_sock=socket(AF_INET, SOCK_STREAM)
				risp_sock.connect((ipr, pr))
				risp_sock.send("AQUE"+pktId+MY_IP+MY_PORTS+Filemd5+nomeFile)
				risp_sock.close()
		lockPktRic.release()
	
		# se ttl > 1 inoltro ai miei vicini
		if (ttl > 1):
			ttl = ttl - 1
			lockListaNeigh.acquire()
			for i in range(0,len(listaNeigh)):
				#non invio al vicino nel caso questo sia quello che mi ha mandato il pacchetto o quello che ha creato per primo il pacchetto
				if (listaNeigh[i] != ipr and listaNeigh[i] != ip):
					risp_sock=socket(AF_INET6, SOCK_STREAM)
					risp_sock.connect((listaNeigh[i], listaPort[i]))
					risp_sock.send("QUER"+pktId+ipr+pr+ttl_send+search_str)
					risp_sock.close()
			lockListaNeigh.release()


# funzione vicini
def nears(s, ip, p):
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	pktId = s.recv(16)
	ipr = s.recv(39)
	tpr =s.recv(5)
	print "aaa"+tpr
	pr = int(tpr)
	ttl = int(s.recv(2))
	ttl_send = "%02d" % ttl
	now = time.time()
	#controllo pacchetto
	if (control_packet(pktId) == 0):
		#rispondo
		lockPktRic.acquire()
		pktRic.append(st.structPktId(pktId, now))
		risp_sock=socket(AF_INET6, SOCK_STREAM)
		risp_sock.connect((ipr, pr))
		risp_sock.send("ANEA"+pktId+MY_IP+MY_PORTS)
		risp_sock.close()
		lockPktRic.release()
	
	
	if (ttl > 1):
			#inoltro
			ttl = ttl - 1
			ttl_send = "%02d" % ttl
			lockListaNeigh.acquire()
			for i in range(0,len(listaNeigh)):
				if (listaNeigh[i] != ipr and listaNeigh[i] != ip):
					risp_sock=socket(AF_INET6, SOCK_STREAM)
					risp_sock.connect((listaNeigh[i], int(listaPort[i])))
					risp_sock.send("NEAR"+pktId+ipr+tpr+ttl_send)
					risp_sock.close()
			lockListaNeigh.release()
	
	
# funzione download
def retrs(s, ip, p):
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	md5 = s.recv(16)
	dirs = os.listdir( path )
	m = hashlib.md5()
	file_name = path+"/"+files
	for files in dirs:
		data = open(file_name,'rb').read()
		m.update(data)
		Filemd5 = "%16s" % m.digest()
		#cerco file richiesto e lo invio
		if (Filemd5 == md5):
			#risp_sock=socket(AF_INET6, SOCK_STREAM)
			#risp_sock.connect((ip, p))
			size = os.path.getsize(file_name)
			numchunk = (size/lenchunk) + 1
			cmd = "%04s" %'ARET'
			nchunk = "%06i" % numchunk
			peersock.sendall(cmd + nchunk)
			h = open(file_name, 'rb')
			for i in range(0, numchunk) :
				data = h.read(lenchunk)
				len_i="%05i" % len(data)
				#risp_sock.sendall(len_i)
				#risp_sock.sendall(data)
				s.sendall(len_i)
				s.sendall(data)
			h.close()
			#risp_sock.close()
			s.close()


# gestione risposta ricerca
def aques(s, ip, p):
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	pktId = s.recv(16)
	ipPeer = s.recv(39)
	pPeer = s.recv(5)
	md5 = s.recv(16)
	fileName = s.recv(100)
	lockAttesaRisp.acquire()
	tAttesaRisp = attesaRisp
	tTempoAttesaRisp = tempoAttesaRisp
	lockAttesaRisp.release()
	# se pcktId da considerare e timoeout valido
	if (tAttesaRisp == pktId and tTempoAttesaRisp + TIMEOUT >= time.time()):
		#chiedo lock
		lockListRis.acquire()
		#ricontrollo pcktId
		if (attesaRisp == pktId):
			#aggiungo risposta a vettore risultati e stampo a video
			listaRis.append(st.structRis(pktId, ipPeer, pPeer, md5, fileName))
			print len(listaRis),"). Nome File: ",fileName.strip()
			print "		Ip: ",ipPeer," Port: ",pPeer
		lockListRis.release()
		# se timeout non valido cancello variabili di attesa risposta
	elif (tAttesaRisp == pktId and tTempoAttesaRisp + TIMEOUT < time.time()):
		lockAttesaRisp.acquire()
		attesaRisp = ""
		tempoAttesaRisp = 0
		print "Timeout superato, smetto ricezione risultati"
		lockAttesaRisp.release()
	

# gestione risposta vicini
def aneas(s, ip, p):
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	pktId = s.recv(16)
	ipPeer = s.recv(39)
	pPeer = s.recv(5)
	lockAttesaVicini.acquire()
	tAttesaVicini = attesaVicini
	tTempoAttesaVicini = tempoAttesaVicini
	lockAttesaVicini.release()
	lockListaNeigh.acquire()
	#print len(listaNeigh)," < ",maxNeigh
	
	#se ho meno di max numero vicini 
	if ( len(listaNeigh) < maxNeigh):
		now = time.time()
		#print pktId," == ",tAttesaVicini," and ",tTempoAttesaVicini," + ",TIMEOUT," > ",now
		
		#se pacchetto valido aggiungo
		if (pktId == tAttesaVicini and tTempoAttesaVicini + TIMEOUT > now):
			listaNeigh.append(ipPeer)
			listaPort.append(pPeer)
			print "[SERVER] Aggiunto nuovo vicino"
			print "		ip: "+ipPeer+" port: "+pPeer
	lockListaNeigh.release()
	
	
	

# ---------------------------------------------------------------------

# ---------------------------------------------------------------------				
# funzioni "client"
#
#ricerca con download
def querc():
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	searchc=raw_input("Inserisci nome file da ricercare:\n")
	searchc="%20s" %(searchc)
	ttlc=raw_input("Inserisci il numero di salti:\n")
	ttlc="%02s" % (ttlc)
	pktId = st.pktId()
	pkt="QUER",pktId,MY_IP,MY_PORTS,ttlc,searchc
	
	try:
		lockListaNeigh.acquire()
		#invio pacchetto ai vicini
		for i in range(0,len(listaNeigh)):
			if (listaNeigh[i] != ipr and listaNeigh[i] != ip):
				risp_sock=socket(AF_INET6, SOCK_STREAM)
				risp_sock.connect((listaNeigh[i], listaPort[i]))
				risp_sock.sendall(pkt)
				risp_sock.close()
		lockListaNeigh.release()
		lockListRis.acquire()
		#azzero lista risultati
		listaRis = []
		lockListRis.release()
		lockAttesaRisp.acquire()
		#setto variabili con pacchetti da considerare
		attesaRisp = pktId
		tempoAttesaRisp = time.time()
		lockAttesaRisp.release()
		scelta = "2"
		while (scelta == "2"):
			#mi metto in attesa di comando utente
			print "Di seguito verranno visualizzati i risultati. Premere qualunque tasto per bloccare la ricezione"
			raw_input()
			#chiedo lock su lista ris (quando ho lock non verrà aggiornata)
			lockListRis.acquire()
			#chiedo utente cosa fare
			print "\n1) esegui download\n2) riprendi ricerca\n3) esci senza download\n"
			scelta = raw_input("Inserisci il numero corrispondente al comando desiderato\n")
			if (scelta == 1):
				#richiesta download
				print "digita numero file da scaricare"
				fileDaScaricare = raw_input()
				pkt = "RETR"+listaRis[fileDaScaricare - 1].md5
				risp_sock=socket(AF_INET6, SOCK_STREAM)
				risp_sock.connect((listaRis[fileDaScaricare - 1].ip, int(listaRis[fileDaScaricare - 1].port)))
				risp_sock.send(pkt)
				ack = risp_sock.recv(4)
				#download
				if (ack == "ARET"):
					print "inizio download"
					nChunk = risp_sock.recv(6)
					print "\n Numero di chunck = " + numchunk
					rangeChunk = range (0,int(nChunk))
					fileRic = ''
					for i in rangeChunk:
						lenChunk = risp_sock.recv(5)
						#while len(lenchunk_i) < 5 :
							#lenchunk_i += p.recv(1)
						print "\nLunghezza ", i, "-esimo chunk: ", lenChunk
						data = risp_sock.recv(int(lenChunk))
						#while len(data) < int(lenchunk_i) :
							#data += p.recv(1)
						fileRic += data
					out_file=open(path+"/"+listaRis[fileDaScaricare - 1].nameF,"wb")
					out_file.write(recvd)
					out_file.close()
				
				#azzero variabili attesa pacchetto
				risp_sock.close()
				lockAttesaRisp.acquire()
				attesaRisp = ""
				tempoAttesaRisp = 0
				lockAttesaRisp.release()
				lockListRis.acquire()
				listaRis = []
				lockListRis.release()
				
			if (scelta == 3):
				#azzero variabili attesa pacchetto
				lockAttesaRisp.acquire()
				attesaRisp = ""
				tempoAttesaRisp = 0
				lockAttesaRisp.release()
				lockListRis.acquire()
				listaRis = []
				lockListRis.release()
	except error, msg:
		s = None
		print "ERROR: " , msg

# richiesta vicino

def nearc():
	
	global listaNeigh
	global listaPort
	global attesaVicini
	global tempoAttesaVicini
	global listaRis
	global pktRic
	global attesaRisp
	global tempoAttesaRisp
	global maxNeigh
	
	pktId = st.pktId()
	lockAttesaVicini.acquire()
	attesaVicini = pktId
	tempoAttesaVicini = time.time()
	lockAttesaVicini.release()
	print "all: "+"NEAR"+pktId+MY_IP+MY_PORTS+"2"
	lockListaNeigh.acquire()
	#invio richieste ai vicini
	for i in range(0,len(listaNeigh)):
		risp_sock=socket(AF_INET6, SOCK_STREAM)
		risp_sock.connect((listaNeigh[i], int(listaPort[i])))
		risp_sock.send("NEAR"+pktId+MY_IP+MY_PORTS+"2")
		risp_sock.close()
	#azzero lista vicini
	listaNeigh = []
	listaPort = []
	lockListaNeigh.release()
	
	
	
	
	
	
	

	
# ---------------------------------------------------------------------
# "switch case server"
opts = { "QUER" : quers,
		 "NEAR" : nears,
		 "RETR" : retrs,
		 "AQUE" : aques,
		 "ANEA" : aneas}
		 
# "switch case client"
optc = { "1" : querc,
		 "2" : nearc,
		 "3" : exit}	 
# ---------------------------------------------------------------------



# main

# lancio thread di ascolto
add = "1"



t.start_new_thread(handler_listener, ())

#Inserimento manuale vicini
#~ while (add == "1"):
	#~ Neigh = raw_input("inserire ip")
	#~ Port = raw_input("inserire porta")
	#~ listaNeigh.append(Neigh)
	#~ listaPort.append(Port)
	#~ add = raw_input("digita 1 per inserire altro vicini, qualunque altra cosa per non inserire")
listaNeigh.append("fd00:0000:0000:0000:26fd:52ff:fe7a:6c5a")
listaNeigh.append("fd00:0000:0000:0000:22c9:d0ff:fe47:70a3")
listaPort.append("05000")
listaPort.append("05000")
for i in range(0,len(listaNeigh)):
	print listaNeigh[i]+ " "+ listaPort[i]
	
#gestione comandi utente
cmd=""
while(cmd!="esci"):
	# menu client
	print "\n1) ricerca\n2) vicini\n3) esci\n"
	cmd=raw_input("Inserisci il numero corrispondente al comando desiderato\n")
	optc[cmd]()
