import sys
import os
import json


#----------------------------------CLASSES---------------------------------

class Router:
    def __init__(self, id, x, y, z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z

# Router mobile di cui voglio arrivare a stimare le coordinate spaziali (x,y,z)
class Client:
    def __init__(self, x, y, z, alpha):
        self.x = x
        self.y = y
        self.z = z
        self.alpha = alpha #angolo in inclinazione del client rispetto al piano orizzontale
        #userò alpha solo per capire come orientare i raggi uscnenti dal client


# Ray a.k.a. semiretta (tutti i raggi partono dal client)
class Ray:
    def __init__(self, id, azimuth, elevation, power):
        self.id = id #ogni raggio appartiene ad un router
        self.azimuth = azimuth
        self.elevation = elevation
        self.power = power #lo userò come peso per il calcolo delle coordinate

#----------------------------------FUNCTIONS---------------------------------

# Funzione di controllo argomenti passati da linea di comando
def check_args():
    #controllo numero di argomenti
    if len(sys.argv) != 3:
        print("Usage: python3 triangulation.py <percorso file json della misura> <percoso file json delle posizioni dei router>")
        exit(1)

    #controllo che i file json esistano
    if not os.path.exists(sys.argv[1]):
        print("Il file json della misura non esiste")
        exit(1)
    if not os.path.exists(sys.argv[2]):
        print("Il file json delle posizioni dei router non esiste")
        exit(1)


# Funzione che restituisce la ground truth del client
def get_client_position(measures_file):
    with open(measures_file) as f:
        data_m = json.load(f)

    client_coordinates = data_m["client_ground_truth"]
    return client_coordinates

# Funzione che crea la lista dei router
def get_routers(routers_file):
    with open(routers_file) as f:
        routers_from_json = json.load(f)

    routers = []
    #nota che nel file json i router non sono in un array e ognuno di loro ha la chiave "id"
    for router in routers_from_json:
        r = Router(router["id"], router["x"], router["y"], router["z"])
        routers.append(r)

    return routers



#----------------------------------MAIN---------------------------------

#controllo argomenti
check_args()

#recupero ground truth del client
real_client_coordinates = get_client_position(sys.argv[1])

 

#----------------------------------PLOT---------------------------------


#----------------------------------END---------------------------------

