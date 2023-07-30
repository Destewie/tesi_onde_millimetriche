import numpy as np
from scipy.optimize import minimize
import sys
import os
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

#----------------------------------MAIN----------------------------------

#controllo argomenti passati da linea di comando
check_args()

#crea la lista di sfere
spheres = get_spheres_from_json(sys.argv[1], sys.argv[2])

# Calcolo del punto più probabile di intersezione delle sfere
intersection_point = optimize_distance(spheres)
print("Estimated point:", intersection_point)
print("Real point: [4.44, 2, 0.93]")

#print point to point distance between the estimated point and (4.44, 2, 0.93)
print("Distanza tra il punto stimato e la ground truth: ", np.linalg.norm(intersection_point - np.array([4.44, 2, 0.93])))


#----------------------------------PLOT----------------------------------

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot dei centri delle sfere come tondini blu
for sphere in spheres:
    ax.scatter(sphere.x, sphere.y, sphere.z, c='blue', marker='o')

# plot del client prendendo la ground truth dal file
client_coordinates = get_ground_truth(sys.argv[1])
ax.scatter(client_coordinates["x"], client_coordinates["y"], client_coordinates["z"], c='green', marker='o')

# Plot del punto stimato come "x" rossa
ax.scatter(intersection_point[0], intersection_point[1], intersection_point[2], c='red', marker='x')

# Etichette degli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
