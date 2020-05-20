import logging
import socket
from bitstring import BitArray, BitStream, ConstBitStream
from pprint import pprint
from time import sleep, time
import coords
from pprint import pprint

logging.basicConfig(level=logging.DEBUG, format="%(filename)s: %(funcName)s - %(levelname)s: %(message)s")

class Telescope_Client():
    def __init__(self, connection) :       
        self.connexion_avec_client,self.connexionInfo = connection

    def handle_close(self):
        logging.debug("Disconnected")        
        self.connexion_avec_client.close()

    def act_pos(self, ra, dec):
        (ra_p, dec_p) = coords.rad_2_stellarium_protocol(ra, dec)
        msize = '0x1800'
        mtype = '0x0000'
        localtime = ConstBitStream(str.replace('int:64=%r' % time(), '.', ''))
        #print "move: (%d, %d)" % (ra, dec)
 
        sdata = ConstBitStream(msize) + ConstBitStream(mtype)
        sdata += ConstBitStream(intle=localtime.intle, length=64) + ConstBitStream(uintle=ra_p, length=32)
        sdata += ConstBitStream(intle=dec_p, length=32) + ConstBitStream(intle=0, length=32)
        logging.debug(f"ra : {ra} - dec : {dec}")
        return sdata

    def handle_read(self):
        #format: 20 bytes in total. Size: intle:16
        #Incomming messages comes with 160 bytes..
        data0 = self.connexion_avec_client.recv(160)
        if data0:            
            data = ConstBitStream(bytes=data0, length=160)
            #print "All: %s" % data.bin
 
            msize = data.read('intle:16')
            mtype = data.read('intle:16')
            mtime = data.read('intle:64')
 
            # RA: 
            ant_pos = data.bitpos
            ra = data.read('hex:32')
            data.bitpos = ant_pos
            ra_uint = data.read('uintle:32')
 
            # DEC:
            ant_pos = data.bitpos
            dec = data.read('hex:32')
            data.bitpos = ant_pos
            dec_int = data.read('intle:32')
 
            logging.debug("Size: %d, Type: %d, Time: %d, RA: %d (%s), DEC: %d (%s)" % (msize, mtype, mtime, ra_uint, ra, dec_int, dec))
            (sra, sdec, stime) = coords.eCoords2str(float("%f" % ra_uint), float("%f" % dec_int), float("%f" %  mtime))
            pprint((sra, sdec, stime))
 
            #Sends back the coordinates to Stellarium
            coordonnesFictive = ("6h50m54s","41º58'10''")
            byte = self.act_pos(coords.hourStr_2_rad(coordonnesFictive[0]), coords.degStr_2_rad(coordonnesFictive[1]))

            while True : 
                try : 
                    logging.debug(f"Nouvel coordonnées : sra : {sra} and sdec = {sdec}")
                    self.connexion_avec_client.send(byte.bytes)
                    sleep(1)
                except KeyboardInterrupt : 
                    logging.debug("bye bye")
                    exit()
            
            
            
            




class Telescope_Server():
    def __init__(self, port=10001):
        self.port = port
    
    def run(self):
        hote = ''
        port = self.port

        connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion_principale.bind((hote, port))
        connexion_principale.listen(5)
        print(f"Le serveur écoute à présent sur le port {port}")
        tel = Telescope_Client(connexion_principale.accept())
        while True :              
            tel.handle_read()
            

if __name__ == '__main__': 
    try:
        serveur = Telescope_Server()
        serveur.run()
    except KeyboardInterrupt : 
        print("Bye ! ")
