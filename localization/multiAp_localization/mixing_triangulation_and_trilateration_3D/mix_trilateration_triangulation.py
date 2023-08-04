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

# costante per un threshold sotto il quale il raggio non viene considerato
POWER_THRESHOLD = 0.25

#angolo in gradi per ruotare sempre i raggi in modo che gli 0 gradi siano paralleli all'asse Y
ANGLE_OFFSET = 90

# Dimensione della stanza
X_ROOM = 6.442
Y_ROOM = 7.245
Z_ROOM = 2.64

#----------------------------------CLASSES---------------------------------

class Ray:
    def __init__(self, id, azimuth, elevation, length, power, reliable_distance):
        self.id = id #ogni raggio appartiene ad un router
        self.azimuth = azimuth 
        self.elevation = elevation
        self.length = length
        self.power = power #lo userò come peso per il calcolo delle coordinate
        self.reliable_distance = reliable_distance #true se posso fidarmi della distanza
        

class Router:
    def __init__(self, id, x, y, z, tilt, client_tilt, ray):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.client_tilt = client_tilt #lo uso per aggiustare l'orientamento del raggio. Anche lui ha bisongo dell'aggiustamento per il sistema di riferimento comune
        self.tilt = tilt
        self.ray = ray

    # Funzione che mi restituisce il punto finale del raggio che parte dal router
    # tieni a mente che il tilt va a modificare il valore dell'angolo di azimuth
    def get_ray_end_point(self):
        base_angle_for_router = adattamento_angolo(self.tilt)
        azimuth_diff_ap_client = differenza_angoli(base_angle_for_router, adattamento_angolo(self.client_tilt)+180)
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

# Funzione che trasforma un qualsiasi angolo in gradi centigradi in un nuovo angolo in gradi centigradi che rispetti il sistema di riferimento che voglio io
def adattamento_angolo(angolo):
    return ANGLE_OFFSET - angolo

# Funzione che mi prende la ground truth (vere coordinate) del client dal file delle misure
def get_real_client_position(measures_file):
    with open(measures_file) as f:
        data_m = json.load(f)
    client_coordinates = data_m["client_ground_truth"]
    return client_coordinates


# Funzione che crea la lista dei raggi
def get_rays(measures_file):
    with open(measures_file) as f:
        data_m = json.load(f)

    rays = []
    for ray in data_m["measures"]:
        r = Ray(ray["ap_id"], ray["azimuthAngle"], ray["elevationAngle"] , ray["distance"], ray["power"], ray["distance_reliability"])
        rays.append(r)

    return rays

# Funzione che crea la lista dei router
def get_routers(routers_file, rays, client_info):
    with open(routers_file) as f:
        routers_from_json = json.load(f)

    routers = []
    keys = routers_from_json.keys() #lista delle chiavi del dizionario
    for key in keys:
        for ray in rays:
            if ray.id == key:
                r = Router(key, routers_from_json[key]["x"], routers_from_json[key]["y"], routers_from_json[key]["height"], routers_from_json[key]["tilt"], client_info["tilt"], ray)
                routers.append(r)

    return routers

#ritorna il sottoinsieme di router di qulità
def get_reliable_routers(routers):
    reliable_routers = []
    for router in routers:
        if quality_test_router(router):
            reliable_routers.append(router)
    return reliable_routers

#calculate every possible subset of spheres, excluding all the subsets with only one element
def all_subsets_except_single_elements(set_elements):
    all_subsets = chain.from_iterable(combinations(set_elements, r) for r in range(2, len(set_elements)+1))
    return all_subsets

# Funzione del quality test di un router
def quality_test_router(router):
    return (router.ray.power >= POWER_THRESHOLD and router.ray.reliable_distance)

# Funzione che calcola il punto medio pesato degli estremi dei raggi. Questa funzione tenderà ad avvicinare il punto medio all'endpoint dei raggi con potenza maggiore
def get_weighted_midpoint_of_rays_endpoints(routers):
    sum_of_weights = 0
    sum_of_weighted_endpoints = np.array([0.0, 0.0, 0.0])
    print()
    for router in routers:
        sum_of_weights += router.ray.power
        endpoint = router.get_ray_end_point()
        sum_of_weighted_endpoints[0] += float(router.ray.power) * float(endpoint[0])
        sum_of_weighted_endpoints[1] += router.ray.power * endpoint[1]
        sum_of_weighted_endpoints[2] += router.ray.power * endpoint[2]
    sum_of_weighted_endpoints[0] = sum_of_weighted_endpoints[0] / sum_of_weights
    sum_of_weighted_endpoints[1] = sum_of_weighted_endpoints[1] / sum_of_weights
    sum_of_weighted_endpoints[2] = sum_of_weighted_endpoints[2] / sum_of_weights
    return sum_of_weighted_endpoints


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

# Funzione che calcola la distanza tra il punto in input e tutti gli end point dei raggi
def distance_from_endpoints(point, routers):
    distances = 0
    for router in routers:
        if(quality_test_router(router)):
            distances += (np.linalg.norm(point - router.get_ray_end_point()))
    return distances


# Error function to be minimized
def error_function(estimated_client, routers):
    #l'errore è la somma delle distanze tra la posizione stimata e il l'end point di ogni raggio
    error = 0
    for router in routers:
        if(quality_test_router(router)):
            error += np.linalg.norm(estimated_client - router.get_ray_end_point()) * router.ray.power
    return error

# Funzione che mi restituisce la posizione stimata del client tramite la funzione minimize di scipy
def estimate_client_position(routers):
    #inizializzo la posizione stimata del client
    estimated_client = np.array([0, 0, 0])
    #minimizzo la funzione di errore
    result = minimize(
        lambda point: error_function(point, routers), 
        estimated_client, 
        method='BFGS',
    )
    #restituisco la posizione stimata del client
    return result.x


# Funzione che ricava l'errore che avrei con un numero di APs diverso
def get_error_with_different_number_of_aps(routers, real_client_coordinates):
    #ora lancio optimize_distances with every possibile subset of spheres and calculate the distance between it and the ground truth
    router_subsets = all_subsets_except_single_elements(routers) 

    #calcolo il punto che ottimizza la distanza per ogni sottoinsieme di sfere e lo salvo in un dizionario con chiave il numero di sfere nel sottoinsieme
    error_per_subset_dimension = {} #array che conterrà la distanza media tra il punto stimato e la ground truth per ogni numero di sfere nel sottoinsieme
    previous_subset_dimension = 0 #variabile che mi serve per capire se sto affrontando un sottoinsieme di dimensione diversa da quelli precedenti
    number_of_subsets_of_previous_dimension = 0 #contatore di sottoinsiemi di dimensione precedente. serve per poi fare la media

    for subset in router_subsets:
        #il punto stimato per il sottoinsieme che sto considerando
        estimated_point_per_subset = estimate_client_position(subset)
        estimated_point_per_subset = np.array(estimated_point_per_subset)

        #se è la prima volta che affronto un sottoinsieme di dimensione diversa da quelli precedenti, inizializzo il dizionario
        if(len(subset) != previous_subset_dimension):
            #calcolo la distanza media per il numero di sfere del sottoinsieme precedente
            if(number_of_subsets_of_previous_dimension != 0):
                error_per_subset_dimension[previous_subset_dimension] /= number_of_subsets_of_previous_dimension

            previous_subset_dimension = len(subset) #qui la parola "previous" è fuorviante, perché in realtà è il numero di sfere del sottoinsieme che sto considerando
            error_per_subset_dimension[len(subset)] = 0 #inizializzo la distanza media per il numero attuale di sfere per sottoinsieme
            number_of_subsets_of_previous_dimension = 0 #inizializzo il contatore di sottoinsiemi per questa nuova cardinalità di sottoinsiemi

        #mi vado a salvare la distanza tra il punto stimato e la ground truth in un dizionario che come chiave ha il numero di sfere nel sottoinsieme
        error_per_subset_dimension[len(subset)] += np.linalg.norm(estimated_point_per_subset - np.array([real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]]))

        number_of_subsets_of_previous_dimension += 1


    #calcolo la distanza media per l'ultimo numero di sfere (non viene calcolata nel ciclo for)
    error_per_subset_dimension[previous_subset_dimension] /= number_of_subsets_of_previous_dimension

    return error_per_subset_dimension

# Funzione che salva nella stessa cartella del file delle misure un file json contenente il dizionario che gli viene passato
def save_json(dictionary, measures_file):
    folder_path = os.path.dirname(measures_file)
    file_name = "mixed_algorithm_error_per_subset_dimension.json"

    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as outfile:
        json.dump(dictionary, outfile)


#----------------------------------MAIN----------------------------------

#controllo argomenti
check_args()

#do un nome ai file passati in input
measures_file = sys.argv[1]
routers_file = sys.argv[2]

#prendo le coordinate reali del client
real_client_coordinates = get_real_client_position(measures_file)

#prendo i raggi
rays = get_rays(measures_file)

#prendo i router
routers = get_routers(routers_file, rays, real_client_coordinates)


print()

print("---------------------REAL CLIENT INFO---------------------")

#printo la vera posizione del client
print("Vera posizione del client: " + str(real_client_coordinates))

#calcolo la distanza totale tra la vera posizione e tutti gli endpoint dei raggi
print("Quella che segue non so se può essere giustamente interpretata come una misura di errore hardware:")
print("Distanza totale tra la vera posizione e tutti gli endpoint dei raggi: " + str(distance_from_endpoints(np.array([real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]]), routers)))


print()

print("---------------------ESTIMATED CLIENT INFO (MINIMIZATION)---------------------")
#stimo la posizione del client
estimated_client = estimate_client_position(routers)
print("Posizione stimata del client: " + str(estimated_client))

#calcolo l'errore tra la posizione stimata e quella vera stando attento ai tipi dei dati
np_client_coordinates = np.array([real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]])
np_estimated_position = np.array(estimated_client)
error = np.linalg.norm(np_client_coordinates - np_estimated_position)
print("Errore di approssimazione dalla minimizzazione: " + str(error))

#calcolo la distanza totale tra la posizione stimata e tutti gli endpoint dei raggi
print("Distanza totale tra la posizione stimata e gli endpoints dei raggi di qualita': " + str(distance_from_endpoints(estimated_client, routers)))

print()

print("---------------------ESTIMATED CLIENT INFO (WEIGHTED AVERAGE)---------------------")

#prendo il punto medio degli endpoint dei router di qualità
quality_routers = get_reliable_routers(routers)
punto_medio = get_weighted_midpoint_of_rays_endpoints(quality_routers)
print("Posizione stimata del client: " + str(punto_medio))

#calcolo la differenza tra la media degli endpoints e il cilent reale
print("Errore di approssimazione della media pesata: " + str(np.linalg.norm(np_client_coordinates - punto_medio)))

#calcolo la distanza totale tra la posizione stimata e tutti gli endpoint dei raggi
print("Distanza totale tra la posizione stimata e gli endpoints dei raggi di qualita': " + str(distance_from_endpoints(punto_medio, routers)))

print()

print("--------------------OTHER STATS---------------------")

#calcolo l'errore che avrei con un numero di APs diverso
print("Errore medio considerando solo n access points per volta:")
error_per_subset_dimension = get_error_with_different_number_of_aps(get_reliable_routers(routers), real_client_coordinates)
print(error_per_subset_dimension)

#salvo su un file json l'errore che avrei con un numero di APs diverso
save_json(error_per_subset_dimension, sys.argv[1])

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

#plotto una linea lunga uno che parte dal client, è parallela al piano x-y e punta verso client.tilt
#usa real_client_coordinates["tilt"] per capire il punto finale della linea
x = [real_client_coordinates["x"], real_client_coordinates["x"] + math.cos(math.radians(-real_client_coordinates["tilt"] + ANGLE_OFFSET))]
y = [real_client_coordinates["y"], real_client_coordinates["y"] + math.sin(math.radians(-real_client_coordinates["tilt"] + ANGLE_OFFSET))]
z = [real_client_coordinates["z"], real_client_coordinates["z"]]
ax.plot(x, y, z, color='green')

#plotto la posizione stimata del client
ax.scatter(estimated_client[0], estimated_client[1], estimated_client[2], color='red', marker='x')

#plotto il punto medio degli endpoint dei router di qualità
ax.scatter(punto_medio[0], punto_medio[1], punto_medio[2], color='orange', marker='x')

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
