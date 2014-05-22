__author__ = 'stefanoguerra'

# -*- coding: utf-8 -*-

from socket import *
import structSession
import structFile
import string
import thread as thrd
import sys
import math
import re


def controllo_sessione(sid):
    for sessione in listaSessioni:
        if (sessione.sid == sid):
            sessionLogin = 1
            break
    return sessionLogin



def logi(clientSocket):
    global contSessioni
    print "LOGI"
    ip_peer = clientSocket.recv(15)
    porta_peer = clientSocket.recv(5)
    errSessione = 0
    for sessione in listaSessioni:
        if (sessione.pip == ip_peer and sessione.pport == porta_peer):
            errSessione = 1
            break
    if errSessione == 0:
        contSessioni = contSessioni + 1
        sessionId = "%016d" % (contSessioni)
        print sessionId, "", ip_peer, "",porta_peer
        session = structSession.structSession(sessionId, ip_peer, porta_peer)
        listaSessioni.append(session)
    elif errSessione == 1:
        print "-----SESSIONE GIA ESISTENTE-----"
        sessionId = "%016d" % 0
    clientSocket.send("ALGI"+sessionId)


def logo(clientSocket):
    print "LOGO"
    psessionId = clientSocket.recv(16)
    errSessione = controllo_sessione(psessionId)
    nDelete = 0
    if errSessione == 1:

        i = 0

        while i < len(listaFile):
            j = 0
            while j < len(listaFile[i].idsess):

                if (listaFile[i].idsess[j] == psessionId):
                    nDelete = nDelete + 1
                    listaFile[i].idsess.pop(j)
                    print "CANCELLATO--> ", listaFile[i].nome
                    break
                else:
                    j = j + 1

            if (len(listaFile[i].idsess) == 0):
                listaFile.pop(i)
            else:
                i = i +1
        nfile = "%03d" % nDelete
        temp = 0
        for sessione in listaSessioni:
            if (sessione.sid == psessionId):
                listaSessioni.pop(temp)
                break
            temp = temp +1
        clientSocket.send("ALGO"+nfile)
        print "FILE PRESENTI: ", len(listaFile), ", FILE CANCELLATI: ", nDelete
    elif errSessione == 0:
        print "-----SESSIONE NON ESISTENTE-----"



def addr(clientSocket):
    print "ADDR"
    psessionId = clientSocket.recv(16)
    randomId = clientSocket.recv(16) #md5
    lenFile = clientSocket.recv(10)
    lenPart = clientSocket.recv(6)
    nomef = clientSocket.recv(100)
    print lenFile
    print lenPart
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
            for i in range(0,(int(lenFile)/int(lenPart))/8):
                listPart.append(bytearray("11111111"))             
            stringa1=""
            if ((int(math.ceil(float(lenFile)/float(lenPart))) % 8)>0):
            	for indx in range(0,8-(int(math.ceil(float(lenFile)/float(lenPart))) % 8)):
                	stringa1=stringa1+"0"
                for i in range(0,((int(math.ceil(float(lenFile)/float(lenPart))) % 8))):
                	stringa1 = stringa1+"1"
                listPart.append(bytearray(stringa1))
            newFile = structFile.structFile(nomef, randomId, lenFile, lenPart, listPart, psessionId)
            listaFile.append(newFile)
        nPart = str("%08d" %int(math.ceil(float(lenFile)/float(lenPart))))
        print nPart
        clientSocket.send("AADR"+nPart)
    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"



def delf(clientSocket):
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



def look(clientSocket):
    stringa = ""
    print "LOOK"
    psessionId = clientSocket.recv(16)
    searchString = clientSocket.recv(20)
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
    
    while True:
        m = stringa2[:1024]
        clientSocket.send(m)
        stringa2 = stringa2[1024:]
        if len(m) <1024:
            break  
    stringa=""

def fchu(clientSocket):
    stringchu=""
    stringar=""
    print "FCHU"
    psessionId = clientSocket.recv(16)
    rndId = clientSocket.recv(16)
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
                                stringchu = stringchu+str(listaFile[i].partList[h][l])
                                print stringchu
                hitpeer="%03d"%(len(listaFile[i].idsess))              
    elif(sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"

    print stringchu
    stringar="AFCH"+hitpeer+stringchu
    print stringar
    """
    while True:
        m = stringar[:1024]
        clientSocket.send(m)
        stringa2 = stringar[1024:]
        if len(m) <1024:
            break  
    """
    clientSocket.send(stringar)

def rpad(clientSocket):
    print "RPAD"
    psessionId = clientSocket.recv(16)
    rndId = clientSocket.recv(16)
    partNum = clientSocket.recv(8)
    index=0
    tot=-1
    listPart=[]
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        trovato = 0
        for files in listaFile:
            if files.randomId == rndId:					            # trovato file rndId
                for i in range(0,len(files.idsess)):				# scorro gli idsess che hanno quel file
					if (psessionId == files.idsess[i]):	            # se trovo, peer aveva gia parti, devo solo aggiornare
						trovato = 1					                # trovato = devo solo aggiornare
						index = i						            # index = indice di quello che devo aggiornare
						files.partList[index][int(math.floor(int(partNum)/8))][7-((int(partNum)-1)%8)]="1"
                        tot=0
                if (trovato == 0):
                    #se il peer ha appena iniziato a scaricarlo:
                    for i in range(0,(int(files.lenFile)/int(files.lenPart))/8):    #inizializzo a 0
                        listPart.append(bytearray("00000000"))             
                    if ((int(math.ceil(float(lenFile)/float(lenPart))) % 8)>0):
                        listPart.append(bytearray("00000000"))
                    newFile = structFile.structFile(nomef, randomId, lenFile, lenPart, listPart, psessionId)
					files.idsess.append(psessionId)                 # aggiungo sessionid
                    files.partList.append(listPart)                 # aggiungo partlist
                    tot=0		                                    # aggiungo peer ai proprietari
                    files.partList[int(len(files.idsess))-1][int(math.floor(int(partNum)/8))][7-((int(partNum)-1)%8)]="1"
        for j in range(0,int(math.ceil(int(files.lenFile)/int(files.lenPart)))):    #conto gli 1
			for i in range(0,8):
				if (files.partList[index][j][i]=="1"):                              
					tot = tot+1
        numDownload = "%08d" % tot
        clientSocket.send("APAD"+numDownload)

    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"



options = { "LOGI" : logi,
            "LOGO" : logo,
            "ADDR" : addr,
			"FCHU" : fchu,
            "DELF" : delf,
            "LOOK" : look,
            "RPAD" : rpad}


def gestore_connessioni(clientSocket, ipp, portap):
    funct = clientSocket.recv(4)
    options[funct](clientSocket)


PORT=3000
listaSessioni = []
contSessioni = 0
listaFile = []



try:
    socketServer = socket(AF_INET, SOCK_STREAM)
    socketServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socketServer.bind(("",PORT))
    socketServer.listen(10)
except error, msg:
    socketServer = None
    print "ERROR: " , msg

while True:
    clientSocket, address = socketServer.accept()
    print "CONNESSIONE DA ---> ", address

    thrd.start_new_thread(gestore_connessioni, (clientSocket,address[0],address[1])) #socket, ip_peer, porta_peer

