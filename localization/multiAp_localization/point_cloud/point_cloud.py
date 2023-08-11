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


#-------------------CLASSES---------------------

# Classe che rappresenta una misura
class Measure:
    def __init__(self, client_tilt, azimuth_angle, elevation_angle, power, distance):
        self.client_tilt = client_tilt
        self.azimuth_angle = azimuth_angle
        self.elevation_angle = elevation_angle
        self.power = power
        self.distance = distance
        self.endpoint = None
        self.distance_from_client = None


    # Funzione che mi calcola la distanza dal client
    def calculate_endpoint(self, ap_info):
        base_angle_of_router = adattamento_angolo(ap_info["tilt"])

        azimuth_diff_ap_client = differenza_angoli(base_angle_of_router, adattamento_angolo(self.client_tilt)+180)
            
        azimuth_rad = np.radians(base_angle_of_router + azimuth_diff_ap_client - self.azimuth_angle)
        elevation_rad = np.radians(-self.elevation_angle)

        x = ap_info["x"] + self.distance * np.cos(azimuth_rad) * np.cos(elevation_rad)
        y = ap_info["y"] + self.distance * np.sin(azimuth_rad) * np.cos(elevation_rad)
        z = ap_info["height"] + self.distance * np.sin(elevation_rad)

        self.endpoint = np.array([x, y, z])

    # Funzione che mi calcola la distanza dal client
    def calculate_distance_from_client(self, client_info: np.ndarray):
        self.distance_from_client = np.linalg.norm(self.endpoint - client_info)



#-------------------FUNCTIONS---------------------
#ritorna il path di ap_info.json
def get_ap_info_path():
    return os.path.join(os.path.dirname(__file__), "..", ROUTERS_INFO_FILENAME)

#torna il path per il json delle misure
def get_measures_path():
    return os.path.join(os.path.dirname(__file__), "..", PATH_TO_MEASURES_FOLDER, MEASURES_FILENAME)

#torna il path della cartella delle misure
def get_measures_dir():
    return os.path.join(os.path.dirname(__file__), "..", PATH_TO_MEASURES_FOLDER)


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
            measures.append( Measure(measure["client_tilt"], measure["azimuthAngle"], measure["elevationAngle"], measure["power"], measure["distance"]) )
        
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

# Funzione che calcola gli endpoints
def calculate_endpoints(ap_info, measures):
    for measure in measures:
        measure.calculate_endpoint(ap_info)

# Funzione che calcola le distanze dal client
def calculate_distances_from_client(client_info, measures):
    for measure in measures:
        measure.calculate_distance_from_client(client_info)


#-------------------MAIN---------------------

# Prendo le info del client
client_info = get_client_info(get_measures_path())

# Prendo le info sull'access point
ap_info = get_ap_info(get_measures_path(), get_ap_info_path())

# Prendo le misure
measures = get_measures(get_measures_path())

# Calcolo gli endpoint di ogni misura
calculate_endpoints(ap_info, measures)

# Calcolo le distanze dal client di ogni misura
calculate_distances_from_client(client_info, measures)


#-------------------PLOT 2D---------------------

# Creare il grafico 2D
fig = plt.figure(figsize=(10, 6))
ax = fig.figure.add_subplot(1, 1, 1)


# Plotto l'access point come un triangolo blu   
plt.scatter(ap_info["x"], ap_info["y"], c='blue', label='Access Point', marker='^')


# Disegna un rettangolo nero che rappresenta la stanza con X_ROOM e Y_ROOM
plt.plot([0, X_ROOM], [0, 0], 'k-', lw=2)
plt.plot([0, 0], [0, Y_ROOM], 'k-', lw=2)
plt.plot([X_ROOM, X_ROOM], [0, Y_ROOM], 'k-', lw=2)
plt.plot([0, X_ROOM], [Y_ROOM, Y_ROOM], 'k-', lw=2)

# Plotto gli endpoints con colore dipendente da endpoint[2]
for measure in measures:
    plt.scatter(measure.endpoint[0], measure.endpoint[1], c=measure.endpoint[2], marker='o')

x_values = [measure.endpoint[0] for measure in measures]
y_values = [measure.endpoint[1] for measure in measures]
tilt_values = [abs(measure.client_tilt) for measure in measures]

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

# Plotto il client come un quadrato magenta
plt.scatter(client_info[0], client_info[1], c='b', label='Client', marker='s')

# Imposto una legenda per dire che il triangolo è l'access point il quadrato è il client, ma il client viene plottato dopo altra roba
plt.legend(loc='lower left')

# Forza gli assi ad essere sulla stessa scala
plt.axis('equal')

plt.title("Measurements point cloud")

# Impostare etichette degli assi
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')

# Salvo il grafico nella stessa directory del file delle misure
plt.savefig(get_measures_dir() + 'point_cloud.pdf', bbox_inches='tight')

# Mostrare il grafico
plt.show()


#----------------------------------Estimation error ECDF----------------------------------

# Organizza le misure in gruppi con lo stesso client_tilt
grouped_measures = {}
for measure in measures:
    if abs(measure.client_tilt) not in grouped_measures:
        grouped_measures[abs(measure.client_tilt)] = []
    grouped_measures[abs(measure.client_tilt)].append(measure.distance_from_client)

# Calcola l'ECDF per ciascun gruppo di misure
plt.figure(figsize=(10, 6))
for client_tilt, distances in grouped_measures.items():
    n = len(distances)
    x = np.sort(distances)
    y = np.arange(1, n + 1) / n
    plt.step(x, y, label=f'Client Tilt {client_tilt}')

plt.xlabel('Estimation error (m)')
plt.ylabel('ECDF')
plt.title('ECDF with Different Client Tilts')
plt.legend()
plt.grid(True)

# Salvo il grafico nella stessa directory del file delle misure
plt.savefig(get_measures_dir() + 'estimation_error_ecdf.pdf', bbox_inches='tight')

plt.show()


#---------------------------------Ftm accuracy ECDF-----------------------------------

# Raccogli tutti i range misurati dal client
ranges = [measure.distance for measure in measures]

# Calcola l'ECDF
n = len(ranges)
x = np.sort(ranges)
y = np.arange(1, n + 1) / n

plt.figure(figsize=(10, 6))

# Plotta una linea verticale che indica il range vero
real_range = np.linalg.norm(client_info - np.array([ap_info["x"], ap_info["y"], ap_info["height"]]))
plt.axvline(x=real_range, color='red', label='Real range')

# Plot ECDF
plt.step(x, y, label='ECDF')

# Voglio limitare x a 5
plt.xlim(4.75, 4.95)

plt.xlabel('Range (m)')
plt.ylabel('ECDF')
plt.title("FTM accuracy ECDF")

plt.legend(loc='lower right')
plt.grid(True)

# Salvo il grafico nella stessa directory del file delle misure
plt.savefig(get_measures_dir() + 'ftm_accuracy_ecdf.pdf', bbox_inches='tight')

plt.show()

#---------------------------------PLOT DISTANZA-POTENZA---------------------------------

# Ordino measures in base alla distanza dal client
measures.sort(key=lambda measure: measure.distance_from_client)
    
# Creo un array con i tilt
tilt_values = [abs(measure.client_tilt) for measure in measures]

# Creo un array con le distanze dal client
distances = [measure.distance_from_client for measure in measures]

# Creo un array con le potenze
powers = [measure.power for measure in measures]

# Creare il grafico 2D
fig = plt.figure(figsize=(10, 6))
ax = fig.figure.add_subplot(1, 1, 1)

ax.scatter(distances, powers, c=tilt_values, cmap='RdYlGn_r')

# Aggiungere la barra laterale colorata
norm = Normalize(vmin=min(tilt_values), vmax=max(tilt_values))
sm = ScalarMappable(cmap='RdYlGn_r', norm=norm)
sm.set_array([])
fig.colorbar(sm, ax=ax, ticks=[0, 25, 50, 75, 100], label="Client tilt in degrees")


plt.xlabel('Distance from Client (m)')
plt.ylabel('Normalized received power')
plt.title('Distance - Received power Plot')
plt.grid(True)

# Salvo il grafico nella stessa directory del file delle misure
plt.savefig(get_measures_dir() + 'distance_power.pdf', bbox_inches='tight')

plt.show()

