__author__ = 'stefanoguerra'

# -*- coding: utf-8 -*-

from socket import *
from bitarray import bitarray
import structSession
import structFile
import string
import thread as thrd
import sys
import math
import re
import threading

def controllo_sessione(sid):
    for sessione in listaSessioni:
        if (sessione.sid == sid):
            sessionLogin = 1
            break
    return sessionLogin

def conta_possessi(sid):
    tot=0
    for f in listaFile:
        for i in range(0,len(f.idsess)):
            if(sid==f.idsess[i]):
                for p in f.partList[i]:
                    tot=tot+p.count(1)
    return tot

def deauth(sid):
    for f in listaFile:
        for i in range(0,len(f.idsess)):
            if (sid==f.idsess[i]):
                f.idsess.pop(i)
                f.partList.pop(i)
    for s in range(0,len(listaSessioni)):
        if sid==listaSessioni[s].sid:
            listaSessioni.pop(s)


            




def logi(clientSocket,lock):
    global contSessioni
    ip_peer = clientSocket.recv(39)
    porta_peer = clientSocket.recv(5)
    print "RICEVUTO----->"+"LOGI"+ip_peer+porta_peer
    errSessione = 0
    for sessione in listaSessioni:
        if (sessione.pip == ip_peer and sessione.pport == porta_peer):
            errSessione = 1
            break
    if errSessione == 0:
        contSessioni = contSessioni + 1
        sessionId = "%016d" % (contSessioni)
        print sessionId, "", ip_peer, "",porta_peer
        session = structSession.structSession(sessionId, ip_peer, porta_peer, 0, 0)
        listaSessioni.append(session)
    elif errSessione == 1:
        print "-----SESSIONE GIA ESISTENTE-----"
        sessionId = "%016d" % 0
    clientSocket.send("ALGI"+sessionId)
    print "INVIATO ------>"+" ALGI"+sessionId


def logo(clientSocket,lock):
    psessionId = clientSocket.recv(16)
    print "RICEVUTO------>"+"LOGO"+psessionId
    errSessione = controllo_sessione(psessionId)
    nlog = -1
    tot = 0
    partsess=bitarray('')
    if errSessione == 1:
        i = 0
        print "Errore sessione"
        for sess in listaSessioni:
            print "-1"
            print sess.sid
            if (sess.sid==psessionId):
                print "0"
                if (len(sess.owner)>0):
                    nlog = 0
                    for rndIdOwned in sess.owner:
                        print "1"
                        for file in listaFile:
                            print "2"
                            print file.partList
                            complete = bitarray('')
                            distribuited = bitarray('')					#cicla su tutti i file
                            if (file.randomId==rndIdOwned):
                                print "3"				#entro quando file = file che ha aggiunto chi si vuole sloggare
                                for i in range(0,len(file.idsess)):
                                    print "4   "+str(i)				#ciclo su chi ha delle parti (chi lo aggiunge = primo)
                                    if (file.idsess[i] == psessionId):
                                        print "5"			#sono all'indice di chi l'ha aggiunto
                                        print file.partList[i] 
                                        for part in range(0,len(file.partList[i])):
                                            print "6"				#mi salvo tutto il vettore delle parti per confrontarlo
                                            complete.extend(file.partList[i][part])
                                            distribuited.extend('00000000')
                                        print "complete ="+str(complete)
                                        print "distribuited init ="+str(distribuited)
                                    else:
                                        print "7"
                                        for part in file.partList[i]:
                                            print "8"
                                            partsess.extend(part)
                                        print "partsess ="+str(partsess)
                                        print "distribuited ="+str(distribuited)
                                        distribuited = distribuited | partsess
                                        print "dopo or ="+str(distribuited)
                                        partsess=bitarray('')
                                tot=tot+distribuited.count(1)
                                if(distribuited.count(1)==complete.count(1)):
                                    print "9"
                                    nlog=1
                                else:
                                    nlog=0
                                    break
							
        if(nlog==0):
            print "INVIATO------> NLOG"+str("%10d" %int(tot))
            clientSocket.send("NLOG"+str("%10d" %int(tot)))
            nlog=-1
        else:
            print nlog
            print "INVIATO------> ALOG"+str(conta_possessi(psessionId))
            clientSocket.send("ALOG"+str("%10d" %int(conta_possessi(psessionId))))
            deauth(psessionId)
            nlog=-1
								



def addr(clientSocket,lock):
    psessionId = clientSocket.recv(16)
    randomId = clientSocket.recv(16) #md5
    lenFile = clientSocket.recv(10)
    lenPart = clientSocket.recv(6)
    nomef = clientSocket.recv(100)
    print "RICEVUTO------>"+"ADDR"+psessionId+randomId+lenFile+lenPart+nomef
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        filePresente = 0
        nFile = 0
        for files in listaFile:
            if (files.randomId == randomId):
                filePresente = 1
                print "Ehi.... File gia presente, serve nuovo..."


        if (filePresente == 0):
            print "-----AGGIUNGO FILE-----"
            listPart = []
            for i in range(0,int((float(lenFile)/float(lenPart))/8)):
                listPart.append(bitarray('11111111'))             
            stringa1=''
            if ((int(math.ceil(float(lenFile)/float(lenPart))) % 8)>0):
            	for indx in range(0,8-(int(math.ceil(float(lenFile)/float(lenPart))) % 8)):
                	stringa1=stringa1+'0'
                for i in range(0,((int(math.ceil(float(lenFile)/float(lenPart))) % 8))):
                	stringa1 = stringa1+'1'
                listPart.append(bitarray(stringa1))
                print listPart
            newFile = structFile.structFile(nomef, randomId, lenFile, lenPart, listPart, psessionId)
            listaFile.append(newFile)
        nPart = str("%08d" %int(math.ceil(float(lenFile)/float(lenPart))))
        for sessione in listaSessioni:
            if (sessione.sid == psessionId):
                sessione.pown=sessione.pown+int(nPart)
		sessione.owner.append(randomId)
        print "INVIATO ------->"+"AADR"+nPart
        clientSocket.send("AADR"+nPart)
    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"



def delf(clientSocket,lock):
    print "DELF"
    psessionId = clientSocket.recv(16)
    md5 = clientSocket.recv(16)
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        temp = 0
        nFile = 0
        for files in listaFile:
            if files.md5 == md5:
                print "ELIMINO ---> ", files.nome, " ID: ", files.idsess
                
                files.idsess.remove(psessionId)
                nFile = len(files.idsess)
                if nFile == 0:
                    listaFile.pop(temp) #:)
                break
            temp = temp + 1
        nfile = "%03d" % nFile
        clientSocket.send("ADEL"+nfile)
        print "FILE RIMANENTI --->", len(listaFile)
    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE------"



def look(clientSocket,lock):
    stringa = ""
    psessionId = clientSocket.recv(16)
    searchString = clientSocket.recv(20)
    print "RICEVUTO-------->"+"LOOK"+psessionId+searchString
    ss1 = searchString.rstrip()
    ss2 = ss1.lstrip()
    ss = ss2.lower()
    print "ss = ",ss
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        indici = []
        for i in range(len(listaFile)):

            if listaFile[i].nome.lower().count(ss) > 0:
                indici.append(i)
        numRandId = "%03d" % len(indici) #numMd5
    print "numRandId ",numRandId
    if (len(indici) != 0):
        for i in indici:
            stringa = stringa+(listaFile[i].randomId+listaFile[i].nome+listaFile[i].lenFile+listaFile[i].lenPart)
    elif(sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"
    stringa2="ALOO"+numRandId+stringa
    print "INVIATO ------->" + stringa2
    
    while True:
        m = stringa2[:1024]
        clientSocket.send(m)
        stringa2 = stringa2[1024:]
        if len(m) <1024:
            break  
    stringa=""

def fchu(clientSocket,lock):
    stringchu=""
    stringar=""
    psessionId = clientSocket.recv(16)
    rndId = clientSocket.recv(16)
    print "RICEVUTO------>"+"FCHU"+psessionId+rndId
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        indici = []

        for i in range(0,len(listaFile)):

            if (listaFile[i].randomId == rndId):
                for h in range(0,len(listaFile[i].idsess)):
                    for j in range(0,len(listaSessioni)):
                        if (listaFile[i].idsess[h] == listaSessioni[j].sid):
                            stringchu=stringchu+listaSessioni[j].pip+listaSessioni[j].pport
                            for l in range(0,len(listaFile[i].partList[h])):
                                stringchu = stringchu+listaFile[i].partList[h][l].tobytes()
                hitpeer="%03d"%(len(listaFile[i].idsess))              
    elif(sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"

    stringar="AFCH"+hitpeer+stringchu
    print "INVIATO ------->" + stringar
    """
    while True:
        m = stringar[:1024]
        clientSocket.send(m)
        stringa2 = stringar[1024:]
        if len(m) <1024:
            break  
    """
    clientSocket.send(stringar)
	



def rpad(clientSocket,lock):
    lock.acquire()
    global tot
    tot = 0
    print "RPAD"
    psessionId = clientSocket.recv(16)
    rndId = clientSocket.recv(16)
    partNum = clientSocket.recv(8)
    print "RICEVUTO---->"+"RPAD"+psessionId+rndId+partNum
    index=0
    listPart=[]
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        trovato = 0
        for files in listaFile:
            if (files.randomId == rndId):
                for i in range(0,len(files.idsess)):
                    if (psessionId == files.idsess[i]):
                        trovato=1
                        index = i
                        files.partList[i][int(math.floor(float(partNum)/8))][7-((int(partNum))%8)]="1"
                        print files.partList[i]
                if (trovato == 0):
                    #se il peer ha appena iniziato a scaricarlo:
                    for l in range(0,int((float(files.lenFile)/float(files.lenPart))/8)):    #inizializzo a 0
                        listPart.append(bitarray("00000000"))             
                    if ((int(math.ceil(float(files.lenFile)/float(files.lenPart))) % 8)>0):
                        listPart.append(bitarray("00000000"))
                    #newFile = structFile.structFile(nomef, randomId, lenFile, lenPart, listPart, psessionId)
                    files.idsess.append(psessionId)                 # aggiungo sessionid
                    files.partList.append(listPart)                 # aggiungo partlist
                    index=len(files.idsess)-1		               
                    files.partList[int(len(files.idsess))-1][int(math.floor(int(partNum)/8))][7-((int(partNum))%8)]="1"
	#print files.partList[index]
                for j in range(0,int(math.ceil((float(files.lenFile)/float(files.lenPart)) / 8))):    #conto gli 1
                    print files.partList[index][j]
                    print j
                    tot=tot+files.partList[index][j].count(1)
        numDownload = "%08d"%tot
	print "INVIATO ------->" + "APAD" + numDownload
        clientSocket.send("APAD"+numDownload)

    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"
    lock.release()



options = { "LOGI" : logi,
            "LOGO" : logo,
            "ADDR" : addr,
			"FCHU" : fchu,
            "DELF" : delf,
            "LOOK" : look,
            "RPAD" : rpad}


def gestore_connessioni(clientSocket, ipp, portap, lock):
    funct = clientSocket.recv(4)
    options[funct](clientSocket,lock)


PORT=3000
listaSessioni = []
contSessioni = 0
listaFile = []



try:
    socketServer = socket(AF_INET6, SOCK_STREAM)
    socketServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socketServer.bind(("",PORT))
    socketServer.listen(10)
except error, msg:
    socketServer = None
    print "ERROR: " , msg

global lock 
lock = threading.Lock()

while True:
    clientSocket, address = socketServer.accept()
    print "CONNESSIONE DA ---> ", address

    thrd.start_new_thread(gestore_connessioni, (clientSocket,address[0],address[1],lock)) #socket, ip_peer, porta_peer

