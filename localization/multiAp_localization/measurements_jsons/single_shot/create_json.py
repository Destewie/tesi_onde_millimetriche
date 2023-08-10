#create a json in questo modo:
#{
#    "client_tilt": ,
#    "azimuthAngle": x,
#    "elevationAngle": y,
#    "power": z,
#    "distance": d
#}, ...
#dove x, y, z, d sono valori presenti in file contenuti in una directory

import os
import json
import math

MEASURES_PATH = "/home/des/Desktop/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-08-08_measurements/"

MAIN_PATH_JSON_PATH = "/processed_data/md_track/mainPathInfo.txt"

NEW_JSON_PATH = "/home/des/Documents/università/tesi_onde_millimetriche/localization/multiAp_localization/measurements_jsons/single_shot/nuovo_json.json"

nuove_entries = []

#prendo os.listdir(MEASURES_PATH). i risultati saranno v1, v2, v3, ... , v32, v33, v90. Li voglio ordinati così
lista = os.listdir(MEASURES_PATH)
lista.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
print(lista)

#vado a scorrere tutte le cartelle in measures_path
for folder in lista:
    #mi prendo il nome del folder e faccio un unico path comprendendo measures_path + nome folder + main_path_json_path
    measure_json_path = MEASURES_PATH + folder + MAIN_PATH_JSON_PATH

    #apro il file json
    with open(measure_json_path) as json_file:
        #carico il file json in un dizionario
        data = json.load(json_file)

        #creo una entry per il json
        entry = {
            "client_tilt": folder,
            "azimuthAngle": data["azimuthAngle"],
            "elevationAngle": data["elevationAngle"],
            "power": data["power"],
            "distance": data["distance"]
        }
        nuove_entries.append(entry)


#trasformo la lista di dizionari in un json
json_object = json.dumps(nuove_entries, indent = 4)


#scrivo il json in un file
with open(NEW_JSON_PATH, "w") as outfile:
    outfile.write(json_object)








