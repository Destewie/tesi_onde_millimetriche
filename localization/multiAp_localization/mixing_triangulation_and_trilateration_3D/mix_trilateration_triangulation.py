import numpy as np
from scipy.optimize import minimize
import sys
import os
import json
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import combinations, chain

#----------------------------------CONSTANTS--------------------------------------
#angolo in gradi per ruotare sempre i raggi in modo che gli 0 gradi siano paralleli all'asse Y
ANGLE_OFFSET = 90

# Dimensione della stanza
X_ROOM = 6.442
Y_ROOM = 7.245
Z_ROOM = 2.64

#----------------------------------CLASSES---------------------------------

class Ray:
    def __init__(self, id, azimuth, elevation, length, power):
        self.id = id #ogni raggio appartiene ad un router
        self.azimuth = azimuth 
        self.elevation = elevation
        self.length = length
        self.power = power #lo userò come peso per il calcolo delle coordinate
        

class Router:
    def __init__(self, id, x, y, z, tilt, client_tilt, ray):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.client_tilt = client_tilt #lo uso per aggiustare l'orientamento del raggio
        self.tilt = tilt
        self.ray = ray

    # angle_offset porta solo ad avere un sistema di riferimento con gli 0 gradi paralleli all'asse Y
    # self.tilt serve per routare i router in modo da rispettare la realtà. (viene messo un - davanti perchè il tilt è negativo)
    def adjust_ray_perspective(self):
        return ANGLE_OFFSET - self.tilt 

    # Funzione che mi restituisce il punto finale del raggio che parte dal router
    # tieni a mente che il tilt va a modificare il valore dell'angolo di azimuth
    def get_ray_end_point(self):
        base_angle_for_router = self.adjust_ray_perspective()
        azimuth_diff_ap_client = differenza_angoli(base_angle_for_router, self.client_tilt)
        azimuth_rad = np.radians(base_angle_for_router + azimuth_diff_ap_client - self.ray.azimuth)
        elevation_rad = np.radians(-self.ray.elevation)
        x = self.x + self.ray.length * np.cos(azimuth_rad) * np.cos(elevation_rad)
        y = self.y + self.ray.length * np.sin(azimuth_rad) * np.cos(elevation_rad)
        z = self.z + self.ray.length * np.sin(elevation_rad)
        return np.array([x, y, z])

#----------------------------------FUNCTIONS--------------------------------------

# Funzione di controllo argomenti passati da linea di comando
def check_args():
    #controllo numero di argomenti
    if len(sys.argv) != 3:
        print("Usage: python3 mixing_triangulation_and_trilateration.py <percorso file json della misura> <percoso file json delle posizioni dei router>")
        exit(1)

    #controllo che i file json esistano
    if not os.path.exists(sys.argv[1]):
        print("Il file json della misura non esiste")
        exit(1)
    if not os.path.exists(sys.argv[2]):
        print("Il file json delle posizioni dei router non esiste")
        exit(1)

# Funzione che mi prende la ground truth (vere coordinate) del client dal file delle misure
def get_real_client_position(measures_file):
    with open(measures_file) as f:
        data_m = json.load(f)
    client_coordinates = data_m["client_ground_truth"]
    return client_coordinates


# Funzione che crea la lista dei raggi
def get_rays(measures_file, client_tilt):
    with open(measures_file) as f:
        data_m = json.load(f)

    rays = []
    for ray in data_m["measures"]:
        r = Ray(ray["ap_id"], ray["azimuthAngle"], ray["elevationAngle"] , ray["distance"], ray["power"])
        rays.append(r)

    return rays

# Funzione che crea la lista dei router
def get_routers(routers_file, rays):
    with open(routers_file) as f:
        routers_from_json = json.load(f)

    routers = []
    keys = routers_from_json.keys() #lista delle chiavi del dizionario
    for key in keys:
        for ray in rays:
            if ray.id == key:
                r = Router(key, routers_from_json[key]["x"], routers_from_json[key]["y"], routers_from_json[key]["height"], routers_from_json[key]["tilt"], real_client_coordinates["tilt"], ray)
                routers.append(r)

    return routers


# Funzione importantissima che mi serve per capire di quanti gradi dovrei tiltare l'ap per avere che punta in modo parallelo ed opposto alla direzione del client
def differenza_angoli(angolo1, angolo2):
    # Converto gli angoli in radianti
    rad_angolo1 = math.radians(angolo1)
    rad_angolo2 = math.radians(angolo2)
    
    # Calcolo la differenza in radianti utilizzando atan2
    diff_rad = math.atan2(math.sin(rad_angolo1 - rad_angolo2), math.cos(rad_angolo1 - rad_angolo2))
    
    # Converto la differenza in gradi
    diff_gradi = math.degrees(diff_rad)
    
    # Assicuriamoci che il risultato sia compreso tra -179 e 180 gradi
    if diff_gradi > 180:
        diff_gradi -= 360
    elif diff_gradi < -180:
        diff_gradi += 360
    
    return -diff_gradi


#----------------------------------MAIN----------------------------------

#controllo argomenti
check_args()

#do un nome ai file passati in input
measures_file = sys.argv[1]
routers_file = sys.argv[2]

#prendo le coordinate reali del client
real_client_coordinates = get_real_client_position(measures_file)

#prendo i raggi
rays = get_rays(measures_file, real_client_coordinates["tilt"])

#prendo i router
routers = get_routers(routers_file, rays)

print()

#printo la vera posizione del client
print("Vera posizione del client: " + str(real_client_coordinates))

#----------------------------------3D PLOT----------------------------------

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#plotto ogni router e il suo raggio
for router in routers:
    #plotto il raggio
    x = [router.x, router.get_ray_end_point()[0]]
    y = [router.y, router.get_ray_end_point()[1]]
    z = [router.z, router.get_ray_end_point()[2]]
    ax.plot(x, y, z, color='b', linewidth=3*router.ray.power)

    #plotto il router (grosso)
    ax.scatter(router.x, router.y, router.z, color='b', s=100)

    #plotto il punto finale del raggio
    ax.scatter(router.get_ray_end_point()[0], router.get_ray_end_point()[1], router.get_ray_end_point()[2], color='b')

#plotto la vera posizione del client
ax.scatter(real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"], color='green')


# Opzionale: Aggiungi etichette agli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Opzionale: Imposta i limiti degli assi
ax.set_xlim([0, X_ROOM])  
ax.set_ylim([0, Y_ROOM]) 
ax.set_zlim([0, Z_ROOM]) 


plt.show()


#----------------------------------END----------------------------------
