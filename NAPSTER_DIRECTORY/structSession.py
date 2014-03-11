# Classe per la gestion della sessione nella directory
class structSession:
    # costruttore
    def __init__(self, sid, pip, pport):
        self.sid = sid
        self.pip = pip
        self.pport = pport
        print "Sessione  creata: ", sid
