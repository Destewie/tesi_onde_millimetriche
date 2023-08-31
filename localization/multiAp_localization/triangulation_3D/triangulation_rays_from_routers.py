import numpy as np
from scipy.optimize import minimize
import sys
import os
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from itertools import combinations, chain

#----------------------------------CONSTANTS AND GLOBALS--------------------------------------

# costante per un threshold sotto il quale il raggio non viene considerato
POWER_THRESHOLD = 0.25

#angolo in gradi per ruotare sempre i raggi in modo che gli 0 gradi siano paralleli all'asse Y
ANGLE_OFFSET = 90

#lunghezza fittizia dei raggi che disegno
RAY_LENGTH = 20

# Dimensione della stanza
X_ROOM = 6.442
Y_ROOM = 7.245
Z_ROOM = 2.64

#vettore vuoto da aggiornare nel tempo
estimate_evolution = []

#----------------------------------CLASSES---------------------------------

class Ray:
    def __init__(self, id, azimuth, elevation, power):
        self.id = id #ogni raggio appartiene ad un router
        self.azimuth = azimuth 
        self.elevation = elevation
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


    def get_ray_start_point(self):
        return np.array([self.x, self.y, self.z])

    # Funzione che mi restituisce il punto finale del raggio che parte dal router
    # tieni a mente che il tilt va a modificare il valore dell'angolo di azimuth
    def get_ray_end_point(self):
        azimuth_rad = np.radians(adattamento_angolo(self.client_tilt)+180 - self.ray.azimuth)
        elevation_rad = np.radians(-self.ray.elevation)
        x = self.x + RAY_LENGTH * np.cos(azimuth_rad) * np.cos(elevation_rad)
        y = self.y + RAY_LENGTH * np.sin(azimuth_rad) * np.cos(elevation_rad)
        z = self.z + RAY_LENGTH * np.sin(elevation_rad)
        return np.array([x, y, z])

    #----------------------------------FUNCTIONS--------------------------------------

# Funzione di controllo argomenti passati da linea di comando
def check_args():
    #controllo numero di argomenti
    if len(sys.argv) != 3:
        print("Usage: python3 triangulation_rays_from_routers.py <percorso file json della misura> <percoso file json delle posizioni dei router>")
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
def get_rays(measures_file):
    with open(measures_file) as f:
        data_m = json.load(f)

    rays = []
    for ray in data_m["measures"]:
        r = Ray(ray["ap_id"], ray["azimuthAngle"], ray["elevationAngle"], ray["power"])
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


# Funzione del quality test di un router
def quality_test_router(router):
    return (router.ray.power >= POWER_THRESHOLD)

# Funzione che trasforma un qualsiasi angolo in gradi centigradi in un nuovo angolo in gradi centigradi che rispetti il sistema di riferimento che voglio io
def adattamento_angolo(angolo):
    return ANGLE_OFFSET - angolo

# Funzione per la distanza client - raggio 
def distance_router_ray(client, ray_starting_point, ray_ending_point):
    line_direction = ray_ending_point - ray_starting_point
    point_to_line_start = client - ray_starting_point

    cross_product = np.cross(line_direction, point_to_line_start)
    numerator = np.linalg.norm(cross_product)
    denominator = np.linalg.norm(line_direction)

    return numerator / denominator


# Funzione errore da minimizzare. Somma solo le distanze tra un punto e tutti i raggi di qualità
def error_function(point, reliable_routers):
    estimate_evolution.append(point) #aggiorno l'evoluzione del punto

    error = 0
    for router in reliable_routers:
        error += distance_router_ray(np.array([point[0], point[1], point[2]]), router.get_ray_start_point(), router.get_ray_end_point()) * router.ray.power

    return error

# Funzione che calcola la distanza media tra il router e ogni raggio di qualità
def average_distance_point_rays(point, reliable_routers):
    total_distance = 0
    for reliable_router in reliable_routers:
        total_distance += distance_router_ray(np.array([point[0], point[1], point[2]]), reliable_router.get_ray_start_point(), reliable_router.get_ray_end_point())

    return total_distance / len(reliable_routers)


# Funzione che trova la posizione stimata del client minimizzando error_function
def find_client_position(reliable_routers):
    #inizializzo la posizione del client
    client_position = np.array([0, 0, 0])

    res = minimize(
            lambda point: error_function(point, reliable_routers), 
            client_position, 
            method='BFGS'
        )

    # x non è la coordinata, ma un oggetto che contiene le coordinate rispetto a tutti gli assi
    return res.x


def update_estimate_evolution(i):
    return estimate_evolution


#calculate every possible subset of spheres, excluding all the subsets with only one element
def all_subsets_except_single_elements(set_elements):
    all_subsets = chain.from_iterable(combinations(set_elements, r) for r in range(2, len(set_elements)+1))
    return all_subsets


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
        estimated_point_per_subset = find_client_position(subset)
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
    file_name = "triangulation_error_per_subset_dimension.json"

    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as outfile:
        json.dump(dictionary, outfile)


def plot_point(point, ax, color):
    ax.scatter(point[0], point[1], point[2], marker='x', color=color)

# Funzione che salva un valore in un file txt nella stessa cartella del file delle misure
def save_txt(value, measures_file):
    folder_path = os.path.dirname(measures_file)
    file_name = "triangulation_error.txt"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as outfile:
        outfile.write(str(value))


#----------------------------------MAIN----------------------------------

#controllo argomenti
check_args()

#do un nome ai file passati in input
measures_file = sys.argv[1]
routers_file = sys.argv[2]

#prendo le coordinate reali del client
real_client_coordinates = get_real_client_position(measures_file) #dizionario
np_client_position = np.array([real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]]) #np array

#prendo i raggi
rays = get_rays(measures_file)

#prendo i router
routers = get_routers(routers_file, rays, real_client_coordinates)

#prendo i router di qualità
reliable_routers = get_reliable_routers(routers)

print()

print("----------------------------CLIENT INFO----------------------------")
#printo la vera posizione del client
print("Vera posizione del client: " + str(real_client_coordinates))
#calcolo l'errore complessivo delle misure
adattamento_posizione_client = [real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"]]
print("Distanza (m) media tra client e le misure (solo router di qualità): " + str(average_distance_point_rays(adattamento_posizione_client, reliable_routers))) 

# calcolo la distanza tra la vera posizione del client e ogni raggio
for router in routers:
    router.distance = distance_router_ray(np_client_position, router.get_ray_start_point(), router.get_ray_end_point())
    print("Distanza (m) tra il client e il raggio " + str(router.id) + ": " + str(router.distance))


print()

print("----------------------------ESTIMATED POINT INFO----------------------------")
#trovo la posizione stimata del client
estimated_client_position = find_client_position(reliable_routers)
np_estimated_position = np.array([estimated_client_position[0], estimated_client_position[1], estimated_client_position[2]])
print("Posizione stimata del client: " + str(estimated_client_position))
print("Router usati per la stima: ", end=" ")
for r in reliable_routers:
    print(r.id, end=" ")
print()
print("Distanza media (m) tra la stima e le misure (solo router di qualità): " + str(average_distance_point_rays(np_estimated_position, reliable_routers))) 

#calcola la distanza tra la stima e tutti i raggi
for router in routers:
    router.distance = distance_router_ray(np_estimated_position, router.get_ray_start_point(), router.get_ray_end_point())
    print("Distanza (m) tra la stima e il raggio " + str(router.id) + ": " + str(router.distance))

print ()


#calcolo la distanza tra la vera posizione del client e la stima
triangulation_error = np.linalg.norm(np_client_position - estimated_client_position)
print("Distanza (m) tra la vera posizione del client e la stima: " + str(triangulation_error))
save_txt(triangulation_error, sys.argv[1])


print()

print("----------------------------OTHER INFO----------------------------")
#calcolo l'errore che avrei con un numero di APs diverso
print("Errore medio (m) considerando solo n access points per volta:")
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

#plotto la vera posizione del client abbastanza grande da essere visibile
ax.scatter(real_client_coordinates["x"], real_client_coordinates["y"], real_client_coordinates["z"], color='green', s=70)

#plotto la stima della posizione del client (big)
ax.scatter(estimated_client_position[0], estimated_client_position[1], estimated_client_position[2], color='red', marker='x', s=70)

#--------------- Animazione ---------------
# Voglio animare la stima della posizione del client usando le posizioni salvate in estimate_evolution
#ani = animation.FuncAnimation(fig, functools.partial(plot_point, ax=ax, color='orange'), frames=estimate_evolution, interval=100, blit=False, repeat=False)

# Salvo l'animazione in un file gif
#ani.save('animation.gif', writer='imagemagick', fps=1)


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

