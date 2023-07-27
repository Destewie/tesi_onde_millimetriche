import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


#classe sfera
class Sphere:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

#funzione per trovare le intersezioni delle sfere
def find_sphere_intersections(spheres):
    intersections = []
    
    for i in range(len(spheres)):
        for j in range(i + 1, len(spheres)):
            A = spheres[i]
            B = spheres[j]
            
            x1, y1, z1, r1 = A.x, A.y, A.z, A.radius
            x2, y2, z2, r2 = B.x, B.y, B.z, B.radius
            
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            
            if distance <= r1 + r2:
                # Calcolo gli angoli di rotazione dei due piani
                angle1 = math.atan2(y2 - y1, x2 - x1)
                angle2 = math.acos((r1 ** 2 + distance ** 2 - r2 ** 2) / (2 * r1 * distance))
                
                # Calcolo le coordinate dei punti di intersezione
                intersection1_x = x1 + r1 * math.cos(angle1 + angle2)
                intersection1_y = y1 + r1 * math.sin(angle1 + angle2)
                intersection1_z = z1 + r1 * math.sin(math.acos((z2 - z1) / distance))
                
                intersection2_x = x1 + r1 * math.cos(angle1 - angle2)
                intersection2_y = y1 + r1 * math.sin(angle1 - angle2)
                intersection2_z = z1 - r1 * math.sin(math.acos((z2 - z1) / distance))
                
                # Aggiungo i punti di intersezione al vettore di risultato
                intersections.append((intersection1_x, intersection1_y, intersection1_z))
                intersections.append((intersection2_x, intersection2_y, intersection2_z))
    
    return intersections


# Esempio di utilizzo
routers_height = 2.44

mik9 = Sphere(0.175, 6.49, routers_height, 4.9026)
mik11 = Sphere(6.077, 0.645, routers_height, 3.2268)
mik13 = Sphere(0.2, 1.19, routers_height, 5.8377)
mik12 = Sphere(2.83, 0.627, routers_height, 4.7901)

spheres = [mik9, mik11, mik13, mik12]
intersections = find_sphere_intersections(spheres)

print(intersections)

# Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot dei centri delle sfere
for sphere in spheres:
    ax.scatter(sphere.x, sphere.y, sphere.z, c='b', marker='o')

# Plot delle intersezioni
for intersection in intersections:
    ax.scatter(intersection[0], intersection[1], intersection[2], c='r', marker='x')

# Impostazioni aggiuntive
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('Centri delle sfere e intersezioni')
plt.grid()
plt.show()