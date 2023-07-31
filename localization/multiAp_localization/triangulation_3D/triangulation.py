import sys
import os
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

#----------------------------------CONSTANTS---------------------------------
# costante per un threshold sotto il quale il raggio non viene considerato
POWER_THRESHOLD = 0.25

#angolo in gradi per ruotare sempre i raggi in modo che gli 0 gradi siano paralleli all'asse Y
ANGLE_OFFSET = 90 

#misure della stanza
X_ROOM = 6.442
Y_ROOM = 7.245
Z_ROOM = 2.64



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
    return client_coordinates #dizionario con chiavi x, y, z, alpha (dove alpha è l'angolo di azimuth del client rispetto al nord del piano cartesiano)

# Funzione che crea la lista dei router
def get_routers(routers_file):
    with open(routers_file) as f:
        routers_from_json = json.load(f)

    routers = []
    keys = routers_from_json.keys() #lista delle chiavi del dizionario
    for key in keys:
        r = Router(key, routers_from_json[key]["x"], routers_from_json[key]["y"], routers_from_json[key]["height"])
        routers.append(r)

    return routers

# Funzione che crea la lista dei raggi
def get_rays(measures_file):
    with open(measures_file) as f:
        data_m = json.load(f)

    rays = []
    for ray in data_m["measures"]:
        r = Ray(ray["ap_id"], ray["azimuthAngle"], ray["elevationAngle"], ray["power"])
        rays.append(r)

    return rays




#----------------------------------MAIN---------------------------------

#controllo argomenti
check_args()

#recupero ground truth del client
real_client_coordinates = get_client_position(sys.argv[1])
 
#recupero lista dei router
routers = get_routers(sys.argv[2])

#recupero lista dei raggi
rays = get_rays(sys.argv[1])



#----------------------------------3D PLOT---------------------------------

#plotto i raggi in 3D con punto di partenza un punto qualsiasi
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#plotto i router
for r in routers:
    ax.scatter(r.x, r.y, r.z, c='blue', marker='o')

#plotto i raggi partendo dal client
start_point = np.array([real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]])

for ray in rays:
    #converto angoli
    azimuth_rad = np.radians(-ray.azimuth - real_client_coordinates["tilt"] + ANGLE_OFFSET)
    elevation_rad = np.radians(ray.elevation)

    line_length = 15 

    #calcolo punto di arrivo del raggio considerando che il client è inclinato di alpha rispetto al piano orizzontale
    end_point = start_point + line_length * np.array([np.cos(azimuth_rad) * np.cos(elevation_rad), 
                                                      np.sin(azimuth_rad) * np.cos(elevation_rad), 
                                                      np.sin(elevation_rad)]) 

    #plotto il raggio
    ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], [start_point[2], end_point[2]], c='red')

#plotto il client
ax.scatter(real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"], c='green', marker='o')

# Opzionale: Aggiungi etichette agli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Opzionale: Imposta i limiti degli assi
ax.set_xlim([0, X_ROOM])  # Sostituisci xmin e xmax con i limiti dell'asse X
ax.set_ylim([0, Y_ROOM])  # Sostituisci ymin e ymax con i limiti dell'asse Y
ax.set_zlim([0, Z_ROOM])  # Sostituisci zmin e zmax con i limiti dell'asse Z


plt.show()

#----------------------------------END---------------------------------

