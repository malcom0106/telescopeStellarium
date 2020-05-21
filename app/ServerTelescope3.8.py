#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import socket
from pprint import pprint
import telescope_client
import time


logging.basicConfig(level=logging.DEBUG, format="%(filename)s: %(funcName)s - %(levelname)s: %(message)s")
#logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind(('', 10001))
connexion_principale.listen(3)
while True :
    #Message d'attente
    logging.info(f"En attente  : Le serveur écoute sur le port 10001")

    connection = None
    try :
        connection, address = connexion_principale.accept()
        logging.info(f"{address} connecté")
    except KeyboardInterrupt : 
        if connection: 
            connection.close()
        break  
    else : 
        tel = telescope_client.Telescope_Client(connection, address)  
        while True : 
            tel.receivemsg()
    