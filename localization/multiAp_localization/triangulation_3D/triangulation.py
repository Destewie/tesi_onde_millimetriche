import sys
import os
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize
import numpy as np
import math

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


# Funzione per la distanza router - raggio con lo stesso id (va usata una funzione di distanza per punto - retta, in cui il segmento che identifica la distanza è sempre perpendicolare alla retta)
def distance_router_ray(router, starting_point, ending_point):
    point = np.array([router.x, router.y, router.z])

    line_direction = ending_point - starting_point
    point_to_line_start = point - starting_point

    cross_product = np.cross(line_direction, point_to_line_start)
    numerator = np.linalg.norm(cross_product)
    denominator = np.linalg.norm(line_direction)

    return numerator / denominator

# Funzione da minimizzare in cui sommo tutte le distanze tra i router e i raggi con lo stesso id
def error_calculation(client, rays, routers):
    #i raggi partono dalla posizione del client
    starting_point = np.array([client[0], client[1], client[2]]) #rispettivamente x, y, z
    line_length = 10 #la lunghezza è ininfluente ai fini del calcolo dell'errore

    error = 0

    #calcolo l'ending point
    for ray in rays:
        #se il raggio ha un power troppo basso non lo considero
        if(ray.power > POWER_THRESHOLD):
            #converto gli angoli in radianti
            azimuth = np.radians(-ray.azimuth + client[3]) #devo sottrarre un alpha (client[3]) per ruotare i raggi. Ricorda che l'algoritmo di minimizzazione avrà da lavorare anche con l'inclinazione del client e non solo con la sua posizione spaziale
            elevation = np.radians(ray.elevation)

            #calcolo l'ending point
            ending_point = starting_point + line_length * np.array([np.cos(azimuth) * np.cos(elevation), 
                                                                    np.sin(azimuth) * np.cos(elevation), 
                                                                    np.sin(elevation)]) 

            #calcolo la distanza tra il router e il raggio con lo stesso id
            for router in routers:
                if(router.id == ray.id):
                    error += distance_router_ray(router, starting_point, ending_point)
                    break

    return error

# Funzione che minimizza l'errore calcolato e ritorna le coordinate del punto in cui l'errore è minimo
def minimize_error(client, rays, routers):
    #inizializzo il punto di partenza
    starting_point = np.array([client.x, client.y, client.z, client.alpha])

    #minimizzo l'errore
    res = minimize(error_calculation, starting_point, args=(rays, routers), method='BFGS')

    #recupero le coordinate del punto in cui l'errore è minimo
    x = res.x[0]
    y = res.x[1]
    z = res.x[2]
    alpha = res.x[3]

    return x, y, z, alpha


#----------------------------------MAIN---------------------------------

#controllo argomenti
check_args()

#recupero ground truth del client
real_client_coordinates = get_client_position(sys.argv[1])
 
#recupero lista dei router
routers = get_routers(sys.argv[2])

#recupero lista dei raggi
rays = get_rays(sys.argv[1])


#minimizzo l'errore
client = Client(0, 0, 0, 0)
x, y, z, alpha = minimize_error(client, rays, routers)

#stampo le coordinate del punto in cui l'errore è minimo
print("Coordinate: " + str(x) + " " + str(y) + " " + str(z))

#stampo l'errore minimo inteso come la distanza tra il punto in cui l'errore è minimo e il punto in cui si trova il client
print("Errore: " + str(np.linalg.norm(np.array([x, y, z]) - np.array([real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]]))))



#----------------------------------3D PLOT---------------------------------

#plotto i raggi in 3D con punto di partenza un punto qualsiasi
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#plotto i router
for r in routers:
    ax.scatter(r.x, r.y, r.z, c='blue', marker='o')

#plotto i veri raggi derivanti dalle misure partendo dal client
start_point = np.array([real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]])
for ray in rays:
    #converto angoli
    azimuth_rad = np.radians(-ray.azimuth - real_client_coordinates["tilt"] + ANGLE_OFFSET) #tocca fare un po' di magheggi se voglio che il plot rispecchi la realtà
    elevation_rad = np.radians(ray.elevation)

    line_length = 15 

    #calcolo punto di arrivo del raggio considerando che il client è inclinato di alpha rispetto al piano orizzontale
    end_point = start_point + line_length * np.array([np.cos(azimuth_rad) * np.cos(elevation_rad), 
                                                      np.sin(azimuth_rad) * np.cos(elevation_rad), 
                                                      np.sin(elevation_rad)]) 

    #plotto il raggio con spessore in base alla power
    ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], [start_point[2], end_point[2]], c='green', linewidth=3*ray.power)

#plotto il vero client
ax.scatter(real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"], c='green', marker='o')

#plotto il client stimato
ax.scatter(x, y, z, c='red', marker='x')

# Opzionale: Aggiungi etichette agli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Opzionale: Imposta i limiti degli assi
ax.set_xlim([0, X_ROOM])  
ax.set_ylim([0, Y_ROOM]) 
ax.set_zlim([0, Z_ROOM]) 


plt.show()

#----------------------------------END---------------------------------

