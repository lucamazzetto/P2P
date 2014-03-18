__author__ = 'stefanoguerra'

# -*- coding: utf-8 -*-

from socket import *
import structSession
import structFile
import thread as thrd
import sys
import re
import string

# Definizione delle variabili globali utilizzate
PORT=3000 #open porta 3000
listSession = []
listFile = []
countSession = 0

# Creazione della socket di tipo server in ascolto per captare connessioni dai client
try:
    s_sock = socket(AF_INET6, SOCK_STREAM)
    s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s_sock.bind(("",PORT))
    s_sock.listen(10)
except error, msg:
    s_sock = None
    print "ERROR: " , msg




# Funzione per il controllo della sessione
def controllo_sessione(sid):
    for ses in listSession:
        if (ses.sid == sid):
            sessionLogin = 1
            break
    return sessionLogin

# Funzione che si occupa del login di un client
def logi(c_sock):
    print "LOGI: richiesta per login."
    ipp2p = c_sock.recv(39) #riceve ip del peer
    pp2p = c_sock.recv(5) #riceve porta del peer
    errorSes = 0
    global countSession
    for ses in listSession:
        if (ses.pip == ipp2p and ses.pport == pp2p):
            errorSes = 1
            break
    if errorSes == 0:
        countSession = countSession + 1
        sessId = "%016d" % (countSession)
        print sessId, "", ipp2p, "",pp2p
        session = structSession.structSession(sessId, ipp2p, pp2p)
        listSession.append(session)
    elif errorSes == 1:
        print "Errore: sessione gia' esistente."
        sessId = "%016d" % 0
    #c_sock.send("ALOG"+sessId)
    c_sock.send("ALGI"+sessId)
#c_sock.send(sessId)

# Funzione che si occupa del logout di un client
def logo(c_sock):
    print "LOGO: richiesta di Logout"
    psessionId = c_sock.recv(16)
    errorSes = controllo_sessione(psessionId)
    nDelete = 0
    if errorSes == 1:
        #ricerca numero file
        i = 0

        #cicla sui file
        # " len(listFile): ", len(listFile)
        while i < len(listFile):
            j = 0
            #print "i",i," len(listFile): ",len(listFile)
            #per ogni file cicla sugli id
            #print len(listFile[i].idsess)
            while j < len(listFile[i].idsess):

                #print "listFile[i].idsess[j]: ",listFile[i].idsess[j]," psessionId: ", psessionId
                if (listFile[i].idsess[j] == psessionId):
                    nDelete = nDelete + 1
                    print "cancellato ", listFile[i].nome
                    listFile[i].idsess.pop(j)
                    break
                else:
                    j = j + 1
            #print "len listidsess: ", len(listFile[i].idsess)

            if (len(listFile[i].idsess) == 0):
                listFile.pop(i)
            else:
                i = i +1
        nfile = "%03d" % nDelete
        temp = 0
        for ses in listSession:
            if (ses.sid == psessionId):
                listSession.pop(temp)
                break
            temp = temp +1
        #c_sock.send("ALGO"+nfile)
        c_sock.send("ALGO"+nfile)
        #c_sock.send(nfile)
        print "File in directory: ", len(listFile), ", cancellati: ", nDelete
    elif errorSes == 0:
        print "Errore: sessione non esistente."

# Funczione che si occupa dell'Aggiunta di un file da parte di un client
def addf(c_sock):
    print "ADDF: richiesta per aggiunta file."
    psessionId = c_sock.recv(16)
    md5 = c_sock.recv(16)
    nomef = c_sock.recv(100)
    #print psessionId, " ",md5,"",nomef
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        filePresente = 0
        nFile = 0
        #ciclo file
        for files in listFile:
            #se trovo stesso md5
            if (files.md5 == md5):
                print "File gia' presente in directory: aggiornamento nome file."
                filePresente = 1
                files.nome = nomef
                trovato = 0
                #ciclare gli idSess
                for i in range(len(files.idsess)):
                    #se trovo lo stesso id
                    if (files.idsess[i] == psessionId):
                        #faccio niente
                        trovato = 1
                        break
                #id non presente
                if (trovato == 0):
                    #lo aggiungo
                    files.idsess.append(psessionId)
                    nFile = len(files.idsess)
                    break
                else:
                    nFile = len(files.idsess)
                    break


        #md5 non presente aggiungo file
        if (filePresente == 0):
            print "File non presente in directory: aggiunta nuovo file."
            newFile = structFile.structFile(nomef, md5, psessionId)
            listFile.append(newFile)
            nFile = 1
        nfile = "%03d" % nFile
        c_sock.send("AADD"+nfile)
    #c_sock.send(nfile)
    elif (sessionLogin == 0):
        print "Errore: sessione non esistente."

# Funzione che si occupa della cancellazione di un file da parte di un client
def delf(c_sock):
    print "DELF: richiesta per rimozione file."
    psessionId = c_sock.recv(16)
    md5 = c_sock.recv(16)
    #controllo sessione
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        temp = 0
        nFile = 0
        #ciclo i file
        for files in listFile:
            #se stesso md5
            if files.md5 == md5:
                print "Elimino file: ", files.nome, " id: ", files.idsess
                
                files.idsess.remove(psessionId)
                nFile = len(files.idsess)
                if nFile == 0:
                    listFile.pop(temp) #:)
                break
            temp = temp + 1
        nfile = "%03d" % nFile
        c_sock.send("ADEL"+nfile)
        #c_sock.send(nfile)
        print "File rimanenti in directory: ", len(listFile)
    elif (sessionLogin == 0):
        print "Errore: sessione non esistente."

# Funzione che si occupa della ricerca di un file all'interno della directory
def fndf(c_sock):
    print "FIND: richiesta di ricerca."
    psessionId = c_sock.recv(16)
    searchString = c_sock.recv(20)
    ss1 = searchString.rstrip()
    ss2 = ss1.lstrip()
    ss = ss2.lower()
    print "ss = ",ss
    #print psessionId, " ", searchString
    # controllo sessione
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        indici = []
        #ciclo file
        for i in range(len(listFile)):
            #se matcho il nome


            if listFile[i].nome.lower().count(ss) > 0:
                indici.append(i)
        #c_sock.send("AFIN")
        nmd5 = "%03d" % len(indici)
    print "nmd5 ",nmd5
    c_sock.send("AFIN"+nmd5)
    #se nMD5 != 0 scrivo il resto
    if (len(indici) != 0):
        for i in indici:
            #c_sock.send(listFile[i].md5+listFile[i].nome)
            #c_sock.send(listFile[i].nome)
            ncopy = "%03d" % len(listFile[i].idsess)
            #print "ncopy ",ncopy
            c_sock.send(listFile[i].md5+listFile[i].nome+ncopy)
            #print listFile[i].md5
            #print listFile[i].md5+listFile[i].nome+ncopy
            print "ncopy ",ncopy
            #ciclo sugli id
            for j in range(len(listFile[i].idsess)):
                #per ogni id lo cerco in listSession
                for z in range(len(listSession)):
                    #se lo trovo invio e passo al nuovo id
                    if listSession[z].sid == listFile[i].idsess[j]:
                        print "Invio ",listSession[z].pip," e porta", listSession[z].pport
                        #c_sock.send(listSession[z].pip)
                        c_sock.send(listSession[z].pip+listSession[z].pport)
                        break
    elif(sessionLogin == 0):
        print "Errore: sessione non esistente."

# Funzione che registra le statistiche di download
def dwnl(c_sock):
    print "DREG: registrazione download."
    psessionId = c_sock.recv(16)
    fileMd5 = c_sock.recv(16)
    #pIp = c_sock.recv(15)
    #pPort = c_sock.recv(5)
    # controllo sessione
    sessionLogin = controllo_sessione(psessionId)
    if (sessionLogin == 1):
        nDL = 0
        for files in listFile:
            if files.md5 == fileMd5:
                files.total = files.total + 1
                nDL = files.total
                print "Numero di download: ", nDL
                break
        if nDL == 0:
            print "Errore: MD5 non presente"
        else:
            #c_sock.send("ARRE")
            ndownl = "%05d" % nDL
            c_sock.send("ADRE"+ndownl)

    elif (sessionLogin == 0):
        print "Errore: sessione non esistente."



# Struttura dati che permette, in base all'identificativo del pacchetto, di richiamare la giusta funzione
options = { "LOGI" : logi,
            "LOGO" : logo,
            "ADDF" : addf,
            "DELF" : delf,
            "FIND" : fndf,
            "DREG" : dwnl}

# Funzione che, in base all'identificativo del pacchetto ricevuto, gestisce le connessioni e le funzioni
def handler_conn(c_sock, ipp, portp):
    funct = c_sock.recv(4)
    options[funct](c_sock)

#=============================================================================================#


# Ciclo per la gestione delle connessioni in arrivo.
while 1:
    #print s_sock
    c_sock, address = s_sock.accept()
    print "Connessione da: ", address
    #stringa= str(address[0])
    #tr=re.split(r'\.',stringa)

    #ipp2p = "%03d.%03d.%03d.%03d" % (int(tr[0]), int(tr[1]), int(tr[2]), int(tr[3]))
    #pp2p = "%05d" % (int(address[1]))

    #print ipp2p
    #print pp2p
    #print len(ipp2p)
    #print len(pp2p)

    thrd.start_new_thread(handler_conn, (c_sock,address[0],address[1])) #socket, ipp2p, pp2p

