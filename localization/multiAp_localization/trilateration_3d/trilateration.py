import numpy as np
from scipy.optimize import minimize
import sys
import os
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import combinations, chain

#----------------------------------CLASS----------------------------------
class Sphere:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

#----------------------------------FUNCTIONS---------------------------------

# Funzione di controllo argomenti passati da linea di comando
def check_args():
    #controllo numero di argomenti
    if len(sys.argv) != 3:
        print("Usage: python3 trilateration.py <percorso file json della misura> <percoso file json delle posizioni dei router>")
        exit(1)

    #controllo che i file json esistano
    if not os.path.exists(sys.argv[1]):
        print("Il file json della misura non esiste")
        exit(1)
    if not os.path.exists(sys.argv[2]):
        print("Il file json delle posizioni dei router non esiste")
        exit(1)

# Funzione che mi prende la ground truth (vere coordinate) del client dal file delle misure
def get_ground_truth(measures_file):
    with open(measures_file) as f:
        data_m = json.load(f)
    client_coordinates = data_m["client_ground_truth"]
    return client_coordinates
    
#calculate every possible subset of spheres, excluding all the subsets with only one element and the subset with all the elements
def all_subsets_except_single_and_full(set_elements):
    all_subsets = chain.from_iterable(combinations(set_elements, r) for r in range(2, len(set_elements)+1))
    return all_subsets

# Funzione che:
# - prende come input due file json che vengono passati da linea di comano: il primo definisce i raggi delle sfere, mentre il secondo contiene le coordinate di ogni sfera
# - restituisce una lista di oggetti di tipo Sphere
def get_spheres_from_json(measures_file, coordinates_file):
    with open(measures_file) as f:
        data_m = json.load(f)
    with open(coordinates_file) as f:
        coordinates = json.load(f)

    #prendo il vettore delle misure dal file
    measures = data_m["measures"]

    spheres = []

    #per ogni misura vado a prendermi la posizione del router dal file e creo una sfera di raggio pari alla distance presente nel file delle misure
    for measure in measures:
        #controllo che la misura della distanza sia affidabile
        if(measure["distance_reliability"] == 1):
            router_info = coordinates[measure["ap_id"]]
            spheres.append(Sphere(router_info["x"], router_info["y"], router_info["height"], measure["distance"]))

    return spheres 

# Funzione di distanza tra un punto e una sfera
def distance_from_point_to_sphere(point, sphere):
    center = np.array([sphere.x, sphere.y, sphere.z])
    dist_squared = abs(np.linalg.norm(point - center) - sphere.radius) ** 2
    return dist_squared


# Funzione di distanza tra un punto e un insieme di sfere
def distance_from_point_to_spheres(point, spheres):
    total_distance_squared = 0
    for sphere in spheres:
        dist_squared = distance_from_point_to_sphere(point, sphere)
        total_distance_squared += dist_squared
    return total_distance_squared


# Funzione di ottimizzazione
def optimize_distance(spheres):
    result = minimize(
        lambda point: distance_from_point_to_spheres(point, spheres),
        x0=np.zeros(3),  # Punto iniziale (assumiamo un punto iniziale [0, 0, 0])
        method='BFGS',  # Metodo di ottimizzazione
    )
    return result.x


# Funzione che ricava l'errore che avrei con un numero di APs diverso
def get_error_with_different_number_of_aps(spheres):
    #ora lancio optimize_distances with every possibile subset of spheres and calculate the distance between it and the ground truth
    sphere_subsets = all_subsets_except_single_and_full(spheres) 

    #calcolo il punto che ottimizza la distanza per ogni sottoinsieme di sfere e lo salvo in un dizionario con chiave il numero di sfere nel sottoinsieme
    error_per_subset_dimension = {} #array che conterrà la distanza media tra il punto stimato e la ground truth per ogni numero di sfere nel sottoinsieme
    previous_subset_dimension = 0 #variabile che mi serve per capire se sto affrontando un sottoinsieme di dimensione diversa da quelli precedenti
    number_of_subsets_of_previous_dimension = 0 #contatore di sottoinsiemi di dimensione precedente. serve per poi fare la media

    for subset in sphere_subsets:
        #il punto stimato per il sottoinsieme che sto considerando
        estimated_point_per_subset = optimize_distance(subset)

        #se è la prima volta che affronto un sottoinsieme di dimensione diversa da quelli precedenti, inizializzo il dizionario
        if(len(subset) != previous_subset_dimension):
            #calcolo la distanza media per il numero di sfere del sottoinsieme precedente
            if(number_of_subsets_of_previous_dimension != 0):
                error_per_subset_dimension[previous_subset_dimension] /= number_of_subsets_of_previous_dimension

            previous_subset_dimension = len(subset) #qui la parola "previous" è fuorviante, perché in realtà è il numero di sfere del sottoinsieme che sto considerando
            error_per_subset_dimension[len(subset)] = 0 #inizializzo la distanza media per il numero attuale di sfere per sottoinsieme
            number_of_subsets_of_previous_dimension = 0 #inizializzo il contatore di sottoinsiemi per questa nuova cardinalità di sottoinsiemi

        #mi vado a salvare la distanza tra il punto stimato e la ground truth in un dizionario che come chiave ha il numero di sfere nel sottoinsieme
        error_per_subset_dimension[len(subset)] += np.linalg.norm(estimated_point_per_subset - np.array([client_coordinates["x"], client_coordinates["y"], client_coordinates["z"]]))

        number_of_subsets_of_previous_dimension += 1


    #calcolo la distanza media per l'ultimo numero di sfere (non viene calcolata nel ciclo for)
    error_per_subset_dimension[previous_subset_dimension] /= number_of_subsets_of_previous_dimension

    return error_per_subset_dimension


# Funzione che salva nella stessa cartella del file delle misure un file json contenente il dizionario che gli viene passato
def save_json(dictionary, measures_file):
    folder_path = os.path.dirname(measures_file)
    file_name = "trilateration_error_per_subset_dimension.json"

    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as outfile:
        json.dump(dictionary, outfile)


#----------------------------------MAIN----------------------------------

#controllo argomenti passati da linea di comando
check_args()

#crea la lista di sfere
spheres = get_spheres_from_json(sys.argv[1], sys.argv[2])


print();

# Calcolo del punto più probabile di intersezione delle sfere
estimated_point = optimize_distance(spheres)
print("Estimated point:", estimated_point)
client_coordinates = get_ground_truth(sys.argv[1])
print("Real point: [",client_coordinates["x"],", ",client_coordinates["y"],", ",client_coordinates["z"],"]")

print ()

#calcolo l'errore che avrei con un numero di APs diverso
print("Errore medio considerando solo n access points per volta:")
error_per_subset_dimension = get_error_with_different_number_of_aps(spheres)
print(error_per_subset_dimension)

#salvo su un file json l'errore che avrei con un numero di APs diverso
save_json(error_per_subset_dimension, sys.argv[1])

#----------------------------------PLOT ESTIMATED POINT----------------------------------

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot dei centri delle sfere come tondini blu
for sphere in spheres:
    ax.scatter(sphere.x, sphere.y, sphere.z, c='blue', marker='o')

# plot del client prendendo la ground truth dal file
ax.scatter(client_coordinates["x"], client_coordinates["y"], client_coordinates["z"], c='green', marker='o')

# Plot del punto stimato come "x" rossa
ax.scatter(estimated_point[0], estimated_point[1], estimated_point[2], c='red', marker='x')

# Etichette degli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()

#----------------------------------END----------------------------------
