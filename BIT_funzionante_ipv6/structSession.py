class structSession:
    def __init__(self, sid, pip, pport, pdwn, pown):
        self.sid = sid
        self.pip = pip
        self.pdwn = pdwn
        self.pown = pown
        self.pport = pport
	self.owner = []
        print "SESSIONE OK ----> ", sid
