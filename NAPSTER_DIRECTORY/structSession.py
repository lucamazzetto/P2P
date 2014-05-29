#NAPSTER GRUPPO 03
# -*- coding: UTF-8 -*-

#guerra 	fd00:0000:0000:0000:22c9:d0ff:fe47:70a3
#mazzetto	fd00:0000:0000:0000:8896:7854:b792:1bd1
#natali 	fd00:0000:0000:0000:7ed1:c3ff:fe76:362a

class structSession:
    def __init__(self, sid, pip, pport):
        self.sid = sid								#session id del peer
        self.pip = pip								#ipv6 del peer
        self.pport = pport							#porta del peer
        print "SESSIONE OK ----> ", sid
