from bitstring import BitArray, BitStream, ConstBitStream
from time import sleep, time
import coords
import logging
from pprint import pprint
import math

class Telescope_Client() :
    def __init__(self, client, address) :       
        self.connexion_avec_client = client
        self.connexionInfo = address  
        self.positionInit = None
        self.positionTelescope = [0.00,0.00]
        self.initTelescope = False
        self.positionCible = None

    def handle_close(self) :
        logging.debug("Disconnected")        
        self.connexion_avec_client.close()

    def act_pos(self, ra, dec) :
        (ra_p, dec_p) = coords.rad_2_stellarium_protocol(ra, dec)
        msize = '0x1800'
        mtype = '0x0000'
        localtime = ConstBitStream(str.replace('int:64=%r' % time(), '.', ''))
        #print "move: (%d, %d)" % (ra, dec)
 
        sdata = ConstBitStream(msize) + ConstBitStream(mtype)
        sdata += ConstBitStream(intle=localtime.intle, length=64) + ConstBitStream(uintle=ra_p, length=32)
        sdata += ConstBitStream(intle=dec_p, length=32) + ConstBitStream(intle=0, length=32)
        return sdata

    def receivemsg(self) :
        try :
            dataRecu = self.connexion_avec_client.recv(160)
        except WindowsError as w : 
            logging.warning(w)
            exit()
        except Exception as ex: 
            logging.warning(ex)
            self.handle_close()
        else :
            if dataRecu is not None :
                logging.debug(dataRecu)
                self.move_telescope(dataRecu)
            
    def send_coordonnnees(self) :
        try : 
            if not self.initTelescope : 
                self.positionTelescope = list(self.positionInit)
                self.initTelescope = True

            byte = self.act_pos(self.positionTelescope[0],self.positionTelescope[1])

            logging.info(f"Nouvel coord. Equ. envoyé a Stellarium : sra : {self.positionTelescope[0]} and sdec = {self.positionTelescope[1]}")
            self.connexion_avec_client.send(byte.bytes)
            sleep(1)
        except WindowsError as w : 
            logging.warning(w)
            exit()
        except Exception as e: 
            logging.warning(e) 

    def read_data(self, mesData):
        #format: 20 bytes in total. Size: intle:16
        #Incomming messages comes with 160 bytes..        
        try : 
            if mesData :
                data = ConstBitStream(bytes=mesData, length=160)
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


                logging.info("Size: %d, Type: %d, Time: %d, RA: %d (%s), DEC: %d (%s)" % (msize, mtype, mtime, ra_uint, ra, dec_int, dec))
                (sra, sdec, stime) = coords.eCoords2str(float("%f" % ra_uint), float("%f" % dec_int), float("%f" %  mtime))
                logging.info(f"Coordonnées Ciblé Par Stellarium : sra : {sra} and sdec = {sdec}")

                if self.positionInit == None : 
                    self.positionInit = self.positionCible = [coords.hourStr_2_rad(sra),coords.degStr_2_rad(sdec)]
                    self.positionInit = tuple(self.positionInit)
                else :
                    self.positionCible = [coords.hourStr_2_rad(sra),coords.degStr_2_rad(sdec)]

        except Exception  as e: 
            print(f"Erreur read_data() : {e}")
            exit()

    def move_telescope(self, data_brut):
        self.read_data(data_brut)
        boolAz = False
        boolHt = False 
        precision = 0.01        
        while True:
            try :                            
                self.send_coordonnnees()
                absAz = self.positionCible[0] - self.positionTelescope[0]
                
                absHt = self.positionCible[1] - self.positionTelescope[1]

                print(f"absAz = {absAz} - absHt = {absHt}")

                if abs(absAz) <= precision :
                    print("Position Azimuthale OK")
                    boolAz = True
                else : 
                    print("Position Azimuthale Pas OK")

                if abs(absHt) <= precision :
                    print("Position Horizontale OK")
                    boolHt = True
                else : 
                    print("Position Azimuthale Pas OK")

                if boolAz and boolHt : 
                    self.receivemsg()

                azi = self.positionTelescope[0] + float(input("az = "))
                haut = self.positionTelescope[1] + float(input("ht = "))
                self.positionTelescope = [azi, haut]
            except Exception as ex :
                logging.warning(ex)
            except KeyboardInterrupt : 
                print("bye !")
                exit()
        self.receivemsg()