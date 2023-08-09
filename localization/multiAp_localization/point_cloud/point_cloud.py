import json
import os
import sys
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

#-------------------CONSTANTS---------------------

ROUTERS_INFO_FILENAME = "ap_info.json"

PATH_TO_MEASURES_FOLDER = "measurements_jsons/single_shot/"
MEASURES_FILENAME = "single_shot_measures.json"

#angolo in gradi per ruotare sempre i raggi in modo che gli 0 gradi siano paralleli all'asse Y
ANGLE_OFFSET = 90

# Dimensione della stanza
X_ROOM = 6.442
Y_ROOM = 7.245
Z_ROOM = 2.64

#-------------------FUNCTIONS---------------------
#ritorna il path di ap_info.json
def get_ap_info_path():
    return os.path.join(os.path.dirname(__file__), "..", ROUTERS_INFO_FILENAME)

#torna il path per il json delle misure
def get_measures_path():
    return os.path.join(os.path.dirname(__file__), "..", PATH_TO_MEASURES_FOLDER, MEASURES_FILENAME)


#prendi info sul ap usato per le misure
def get_ap_info(measures_file_path, routers_info_path):
    with open(measures_file_path) as json_file:
        measure_file_data = json.load(json_file)
        ap_id = measure_file_data["ap_id"]

    with open(routers_info_path) as json_file:
        router_info = json.load(json_file)
        
    return router_info[ap_id]

#prendi info sul client
def get_client_info(measures_file_path):
    with open(measures_file_path) as json_file:
        measure_file_data = json.load(json_file)
        client_info = np.array([measure_file_data["client_ground_truth"]["x"], measure_file_data["client_ground_truth"]["y"], measure_file_data["client_ground_truth"]["z"]])
        
    return client_info


#prendi le misure
def get_measures(measures_file_path):
    measures = []
    with open(measures_file_path) as json_file:
        measure_file_data = json.load(json_file)
        for measure in measure_file_data["measures"]:
            measures.append(measure)
        
    return measures


# Funzione che trasforma un qualsiasi angolo in gradi centigradi in un nuovo angolo in gradi centigradi che rispetti il sistema di riferimento che voglio io
def adattamento_angolo(angolo):
    return ANGLE_OFFSET - angolo


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

# Funzione che prende in input un set di misure e ritorna gli endpoint di ogni misura
def get_endpoints(cilent_info, ap_info, measures):
    base_angle_of_router = adattamento_angolo(ap_info["tilt"])

    endpoints = []
    for measure in measures:
        azimuth_diff_ap_client = differenza_angoli(base_angle_of_router, adattamento_angolo(measure["client_tilt"])+180)
        
        azimuth_rad = np.radians(base_angle_of_router + azimuth_diff_ap_client - measure["azimuthAngle"])
        elevation_rad = np.radians(-measure["elevationAngle"])

        x = ap_info["x"] + measure["distance"] * np.cos(azimuth_rad) * np.cos(elevation_rad)
        y = ap_info["y"] + measure["distance"] * np.sin(azimuth_rad) * np.cos(elevation_rad)
        z = ap_info["height"] + measure["distance"] * np.sin(elevation_rad)

        endpoints.append(np.array([x, y, z]))

    return endpoints

#-------------------MAIN---------------------
# Prendo le info del client
client_info = get_client_info(get_measures_path())

# Prendo le info sull'access point
ap_info = get_ap_info(get_measures_path(), get_ap_info_path())

# Prendo le misure
measures = get_measures(get_measures_path())

# Calcolo gli endpoint di ogni misura
endpoints = get_endpoints(client_info, ap_info, measures)


#-------------------PLOT 3D---------------------

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

# Plotto il client
#ax.scatter(client_info[0], client_info[1], client_info[2], c='green', marker='o')

# Plotto l'access point
#ax.scatter(ap_info["x"], ap_info["y"], ap_info["height"], c='blue', marker='o')

# Plotto gli endpoints
#for endpoint in endpoints:
#    ax.scatter(endpoint[0], endpoint[1], endpoint[2], c='red', marker='o')


# Opzionale: Aggiungi etichette agli assi
#ax.set_xlabel('X')
#ax.set_ylabel('Y')
#ax.set_zlabel('Z')

# Opzionale: Imposta i limiti degli assi
#ax.set_xlim([0, X_ROOM])  
#ax.set_ylim([0, Y_ROOM]) 
#ax.set_zlim([0, Z_ROOM]) 

#plt.show()


#-------------------PLOT 2D---------------------

# Creare il grafico 2D
fig = plt.figure()
ax = fig.figure.add_subplot(1, 1, 1)


# Plotto l'access point
plt.scatter(ap_info["x"], ap_info["y"], c='blue', marker='o')

# Disegna un rettangolo nero che rappresenta la stanza con X_ROOM e Y_ROOM
plt.plot([0, X_ROOM], [0, 0], 'k-', lw=2)
plt.plot([0, 0], [0, Y_ROOM], 'k-', lw=2)
plt.plot([X_ROOM, X_ROOM], [0, Y_ROOM], 'k-', lw=2)
plt.plot([0, X_ROOM], [Y_ROOM, Y_ROOM], 'k-', lw=2)

# Plotto gli endpoints con colore dipendente da endpoint[2]
for endpoint in endpoints:
    plt.scatter(endpoint[0], endpoint[1], c=endpoint[2], marker='o')

x_values = [point[0] for point in endpoints]
y_values = [point[1] for point in endpoints]
tilt_values = [abs(measure["client_tilt"]) for measure in measures]

# Inverto x_values, y_values e tilt_values per avere un plot in cui si vede di più
x_values = x_values[::-1]
y_values = y_values[::-1]
tilt_values = tilt_values[::-1]

scatter = ax.scatter(x_values, y_values, c=tilt_values, cmap='RdYlGn_r')

# Aggiungere la barra laterale colorata
norm = Normalize(vmin=min(tilt_values), vmax=max(tilt_values))
sm = ScalarMappable(cmap='RdYlGn_r', norm=norm)
sm.set_array([])
fig.colorbar(sm, ax=ax, ticks=[0, 25, 50, 75, 100], label="Client tilt in degrees")

# Plotto il client fuksia
plt.scatter(client_info[0], client_info[1], c='magenta', marker='o')

# Impostare etichette degli assi
ax.set_xlabel('X')
ax.set_ylabel('Y')

# Mostrare il grafico
plt.show()

#----------------------------------END----------------------------------




