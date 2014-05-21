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
    ip_peer = clientSocket.recv(39)
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
        #ricerca numero file
        i = 0

        #cicla sui file
        # " len(listaFile): ", len(listaFile)
        while i < len(listaFile):
            j = 0
            #print "i",i," len(listaFile): ",len(listaFile)
            #print len(listaFile[i].idsess)
            while j < len(listaFile[i].idsess):

                #print "listaFile[i].idsess[j]: ",listaFile[i].idsess[j]," psessionId: ", psessionId
                if (listaFile[i].idsess[j] == psessionId):
                    nDelete = nDelete + 1
                    listaFile[i].idsess.pop(j)
                    print "CANCELLATO--> ", listaFile[i].nome
                    break
                else:
                    j = j + 1
            #print "len listidsess: ", len(listaFile[i].idsess)

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
        #clientSocket.send("ALGO"+nfile)
        clientSocket.send("ALGO"+nfile)
        #clientSocket.send(nfile)
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
    #print psessionId, " ",md5,"",nomef
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        filePresente = 0
        nFile = 0
        for files in listaFile:
            if (files.randomId == randomId): #md5
             #   print "----AGGIORNAMENTO NOME FILE-----"
                filePresente = 1
                print "Ehi.... File gia presente, serve nuovo..."
               # files.nome = nomef
                #trovato = 0
                #for i in range(len(files.idsess)):
                #    if (files.idsess[i] == psessionId):
                #        trovato = 1
                #        break
                #if (trovato == 0):
                #    files.idsess.append(psessionId)
                #    nFile = len(files.idsess)
                #    break
                #else:
                #    nFile = len(files.idsess)
                #    break


        if (filePresente == 0):
            print "-----AGGIUNGO FILE-----"
            listPart = []
            test=(int(lenFile)/int(lenPart))/8
            print test
            test1 = range(0,test)
            for i in test1:
                listPart.append("11111111")
            stringa = "00000000"
            stringa1=""
            if ((int(math.ceil(float(lenFile)/float(lenPart))) % 8)>0):
                for i in range(0,((int(math.ceil(float(lenFile)/float(lenPart))) % 8))):
                    stringa1 = stringa1+"1"

                for indx in range(len(stringa1),8):
                    stringa1=stringa1+"0"

                listPart.append(stringa1)
            newFile = structFile.structFile(nomef, randomId, lenFile, lenPart, listPart, psessionId)
            listaFile.append(newFile)
            #nFile = 1
        #rienpio con 0 i primi bit di nPart per arrivare a 8
        nPart = str("%08d" %int(math.ceil(float(lenFile)/float(lenPart))))
        
        #nPart.zfill(8)
        #print int(math.ceil(float(lenFile)/float(lenPart)))
        #print int(lenFile)/int(lenPart)
        print nPart
        clientSocket.send("AADR"+nPart)
    #clientSocket.send(nfile)
    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"



def delf(clientSocket):
    print "DELF"
    psessionId = clientSocket.recv(16)
    md5 = clientSocket.recv(16)
    #controllo sessione
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        temp = 0
        nFile = 0
        #ciclo i file
        for files in listaFile:
            #se stesso md5
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
        #clientSocket.send(nfile)
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
    #print psessionId, " ", searchString
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        indici = []
        for i in range(len(listaFile)):

            if listaFile[i].nome.lower().count(ss) > 0:
                indici.append(i)
        #clientSocket.send("AFIN")
        numRandId = "%03d" % len(indici) #numMd5
    print "numRandId ",numRandId
    #clientSocket.send("AFIN"+numMD5)
    if (len(indici) != 0):
        for i in indici:
            #clientSocket.send(listaFile[i].md5+listaFile[i].nome)
            #clientSocket.send(listaFile[i].nome)
            #numCopie = "%03d" % len(listaFile[i].idsess)
            #print "numCopie ",numCopie
            #clientSocket.send(listaFile[i].md5+listaFile[i].nome+numCopie)
            stringa = stringa+(listaFile[i].randomId+listaFile[i].nome+listaFile[i].lenFile+listaFile[i].lenPart)
            #print listaFile[i].md5
            #print listaFile[i].md5+listaFile[i].nome+numCopie
            #print "numCopie ",numCopie
            #for j in range(len(listaFile[i].idsess)):
                #per ogni id lo cerco in listaSessioni
             #   for z in range(len(listaSessioni)):
                    #se lo trovo invio e passo al nuovo id
              #      if listaSessioni[z].sid == listaFile[i].idsess[j]:
               #         print "Invio ",listaSessioni[z].pip," e porta", listaSessioni[z].pport
                        #clientSocket.send(listaSessioni[z].pip)
                #        stringa = stringa+(listaSessioni[z].pip+listaSessioni[z].pport)
                 #       break
    elif(sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"
    stringa2="ALOO"+numRandId+stringa
    #print stringa2   
    #clientSocket.send("AFIN"+numMD5+stringa)
    #stringa=""
    
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
                                #print stringchu
                hitpeer="%03d"%(len(listaFile[i].idsess))              
    elif(sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"

    print stringchu
    #fino qua va! 20/05
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
    #pIp = clientSocket.recv(15)
    #pPort = clientSocket.recv(5)
    sessionLogin = controllo_sessione(psessionId)
    if(sessionLogin == 1):
        tmp = 0
        trovato = false
        for files in listaFile:
            if files.randomId == rndId:
                for peer in files.idsess:
					if (psessionId == peer):
						trovato = true
						index = tmp
					tmp = tmp+1
                if (trovato == false):
					files.idsess.append(psessionId)
					index = tmp
                files.partList[index][math.floor(files.lenFile/files.lenPart)][(files.lenFile % files.lenPart)-1]="1"
                tot=0
                for j in math.ceil(files.lenFile/files.lenPart):
					for i in range (0,7):
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
    socketServer = socket(AF_INET6, SOCK_STREAM)
    socketServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socketServer.bind(("",PORT))
    socketServer.listen(10)
except error, msg:
    socketServer = None
    print "ERROR: " , msg

while True:
    #print socketServer
    clientSocket, address = socketServer.accept()
    print "CONNESSIONE DA ---> ", address
    #stringa= str(address[0])
    #tr=re.split(r'\.',stringa)

    #ip_peer = "%03d.%03d.%03d.%03d" % (int(tr[0]), int(tr[1]), int(tr[2]), int(tr[3]))
    #porta_peer = "%05d" % (int(address[1]))

    #print ip_peer
    #print porta_peer
    #print len(ip_peer)
    #print len(porta_peer)

    thrd.start_new_thread(gestore_connessioni, (clientSocket,address[0],address[1])) #socket, ip_peer, porta_peer

