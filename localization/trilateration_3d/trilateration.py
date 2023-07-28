import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Sphere:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

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

# Definizione delle sfere
ap_height = 2.44
spheres = [
    Sphere(0.2, 6.055, ap_height, 5.83), #13
    Sphere(2.83, 6.618, ap_height, 4.79), #12
    Sphere(0.175, 0.755, ap_height, 4.9), #9
    Sphere(6, 0.145, ap_height, 3.23), #10
]

# Calcolo del punto più probabile di intersezione delle sfere
intersection_point = optimize_distance(spheres)
print("Punto più probabile di intersezione:", intersection_point)


#stampo la distanza tra ogni sfera e il punto (4.44, 2, 0.93)
for sphere in spheres:
    print("Distanza tra il punto e la sfera: ", distance_from_point_to_sphere(np.array([4.44, 2, 0.93]), sphere))


# Creazione del grafico 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot dei centri delle sfere come tondini blu
for sphere in spheres:
    ax.scatter(sphere.x, sphere.y, sphere.z, c='blue', marker='o')

ax.scatter (4.44, 2, 0.93, c='green', marker='o')
# Plot del punto stimato come "x" rossa
ax.scatter(intersection_point[0], intersection_point[1], intersection_point[2], c='red', marker='x')

# Etichette degli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
