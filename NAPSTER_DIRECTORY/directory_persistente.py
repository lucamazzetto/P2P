#NAPSTER GRUPPO 03
# -*- coding: UTF-8 -*-

#guerra     fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
#mazzetto   fd00:0000:0000:0000:8896:7854:b792:1bd1
#natali     fd00:0000:0000:0000:7ed1:c3ff:fe76:362a

import socket           #libreria per socket
import structSession    #struttura dati sessione
import structFile       #struttura dati file
import string           #manipolazione di stringhe
import thread           #libreria per thread
import sys              #libreria per cartelle
import re               #libreria per espressioni

#Definizione delle variabili utilizzate
PORT=3000
listaSessioni = []
contSessioni = 0
listaFile = []


#funzione per controllo della sessione se presente o meno
def controllo_sessione(sid):
    for sessione in listaSessioni:
        if (sessione.sid == sid):
            sessionLogin = 1
            break
    return sessionLogin


#Lettura e risposta a pacchetto LOGI
def logi(clientSocket):
    global contSessioni
    print "LOGI"
    ip_peer = clientSocket.recv(39)
    porta_peer = clientSocket.recv(5)
    errSessione = 0
    for sessione in listaSessioni:                                                  #controllo se sessione esistente
        if (sessione.pip == ip_peer and sessione.pport == porta_peer):
            errSessione = 1
            break
    if errSessione == 0:                                                            #aggiunta sessione a listaSessioni
        contSessioni = contSessioni + 1
        sessionId = "%016d" % (contSessioni)
        print sessionId, "", ip_peer, "",porta_peer
        session = structSession.structSession(sessionId, ip_peer, porta_peer)
        listaSessioni.append(session)
    elif errSessione == 1:
        print "-----SESSIONE GIA ESISTENTE-----"
        sessionId = "%016d" % 0
    clientSocket.send("ALGI"+sessionId)                                             #invio risposta
    gestore_connessioni(clientSocket,address[0],address[1])


#Lettura richiesta logout e risposta
def logo(clientSocket):
    print "LOGO"
    psessionId = clientSocket.recv(16)
    errSessione = controllo_sessione(psessionId)
    nDelete = 0
    if errSessione == 1:
        i = 0
        while i < len(listaFile):                                                   #ciclo sui file per fare pop dalla listaFile dei file del peer
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
        for sessione in listaSessioni:                                              #pop del peer dalla lista delle sessioni
            if (sessione.sid == psessionId):
                listaSessioni.pop(temp)
                break
            temp = temp +1
        clientSocket.send("ALGO"+nfile)
        print "FILE PRESENTI: ", len(listaFile), ", FILE CANCELLATI: ", nDelete
    elif errSessione == 0:
        print "-----SESSIONE NON ESISTENTE-----"
    gestore_connessioni(clientSocket,address[0],address[1])


#Lettura richiesta aggiunta file e aggiunta a listaFile
def addf(clientSocket):
    print "ADDF"
    psessionId = clientSocket.recv(16)
    md5 = clientSocket.recv(16)
    nomef = clientSocket.recv(100)
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        filePresente = 0
        nFile = 0
        for files in listaFile:                                                     #ciclo sui file, se gia presente aggiorno nome
            if (files.md5 == md5):
                print "----AGGIORNAMENTO NOME FILE-----"
                filePresente = 1
                files.nome = nomef
                trovato = 0
                for i in range(len(files.idsess)):                                  #se file gia presente e gia presente peer, non fa niente
                    if (files.idsess[i] == psessionId):
                        trovato = 1
                        break
                if (trovato == 0):                                                  #se file gia presente ma non il peer, aggiungo il peer 
                    files.idsess.append(psessionId)
                    nFile = len(files.idsess)
                    break
                else:                                                               
                    nFile = len(files.idsess)
                    break
        if (filePresente == 0):                                                     #se file non presente aggiungo a listaFile
            print "-----AGGIUNGO FILE-----"
            newFile = structFile.structFile(nomef, md5, psessionId)
            listaFile.append(newFile)
            nFile = 1
        nfile = "%03d" % nFile
        clientSocket.send("AADD"+nfile)                                             #invio risposta
    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"
    gestore_connessioni(clientSocket,address[0],address[1])


#Lettura richiesta cancellazione file e cancellazione
def delf(clientSocket):
    print "DELF"
    psessionId = clientSocket.recv(16)
    md5 = clientSocket.recv(16)
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        temp = 0
        nFile = 0
        for files in listaFile:                                                     #ciclo sui file e quando li trovo li elimino, aggiornando il numero
            if files.md5 == md5:
                print "ELIMINO ---> ", files.nome, " ID: ", files.idsess
                files.idsess.remove(psessionId)
                nFile = len(files.idsess)
                if nFile == 0:
                    listaFile.pop(temp)
                break
            temp = temp + 1
        nfile = "%03d" % nFile
        clientSocket.send("ADEL"+nfile)                                             #invio risposta
        print "FILE RIMANENTI --->", len(listaFile)
    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE------"
    gestore_connessioni(clientSocket,address[0],address[1])


#Lettura della find, ricerca e risposta con tutti i peer
def fndf(clientSocket):
    stringa = ""
    print "FIND"
    psessionId = clientSocket.recv(16)
    searchString = clientSocket.recv(20)
    ss1 = searchString.rstrip()
    ss2 = ss1.lstrip()
    ss = ss2.lower()
    print "ss = ",ss
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        indici = []
        for i in range(len(listaFile)):                                             #conto i risultati della ricerca su listaFile e mi salvo indici
            if listaFile[i].nome.lower().count(ss) > 0:
                indici.append(i)
        numMD5 = "%03d" % len(indici)
    print "numMD5 ",numMD5
    if (len(indici) != 0):                                                          #se sono presenti risultati salvo md5, nome e numero di copie
        for i in indici:
            numCopie = "%03d" % len(listaFile[i].idsess)
            stringa = stringa+(listaFile[i].md5+listaFile[i].nome+numCopie)
            print "numCopie ",numCopie
            for j in range(len(listaFile[i].idsess)):                               #prendo gli idsess dei peer che hanno file
                for z in range(len(listaSessioni)):                                 #salvo ip e porta dei peer che hanno il file
                    if listaSessioni[z].sid == listaFile[i].idsess[j]:              
                        print "Invio ",listaSessioni[z].pip," e porta", listaSessioni[z].pport
                        stringa = stringa+(listaSessioni[z].pip+listaSessioni[z].pport)
                        break
    elif(sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"
    stringa2="AFIN"+numMD5+stringa
    
    while True:                                                                     #invio la risposta a pezzi di max 1024
        m = stringa2[:1024]
        clientSocket.send(m)
        stringa2 = stringa2[1024:]
        if len(m) <1024:
            break  
    stringa=""      
    gestore_connessioni(clientSocket,address[0],address[1])


#Lettura richiesta di download e aggiornamento del numero di download 
def dwnl(clientSocket):
    print "DREG"
    psessionId = clientSocket.recv(16)
    fileMd5 = clientSocket.recv(16)
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        nDL = 0
        for files in listaFile:                                                     #ricerca del file per aggiornamento numero di download
            if files.md5 == fileMd5:
                files.total = files.total + 1
                nDL = files.total
                print "NUMERO DOWNLOAD: ", nDL
                break
        if nDL == 0:
            print "-----MD5 NON PRESENTE-----"
        else:
            numDownload = "%05d" % nDL
            clientSocket.send("ADRE"+numDownload)                                   #invio risposta

    elif (sessionLogin == 0):
        print "-----SESSIONE NON ESISTENTE-----"
    gestore_connessioni(clientSocket,address[0],address[1])



#Scelgo in base all'identificativo del pacchetto a quale procedura andare
options = { "LOGI" : logi,
            "LOGO" : logo,
            "ADDF" : addf,
            "DELF" : delf,
            "FIND" : fndf,
            "DREG" : dwnl}

#Legge l'id del pacchetto dalla socket 
def gestore_connessioni(c_sock, ipp, portp):
    funct = c_sock.recv(4)
    if funct == "":
        c_sock.close()
    else:    
        options[funct](c_sock)

#Creo la socket in ascolto su porta 3000
try:
    socketServer = socket(AF_INET6, SOCK_STREAM)
    socketServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socketServer.bind(("",PORT))
    socketServer.listen(10)
except error, msg:
    socketServer = None
    print "ERROR: " , msg

#Ciclo infinito per accettare le richieste dai peer 
while True:
    clientSocket, address = socketServer.accept()
    print "CONNESSIONE DA ---> ", address

    thread.start_new_thread(gestore_connessioni, (clientSocket,address[0],address[1]))    #avvio un thread per ogni peer

