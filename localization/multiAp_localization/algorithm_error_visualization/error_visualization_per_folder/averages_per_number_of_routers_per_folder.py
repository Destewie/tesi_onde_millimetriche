import os
from os.path import isdir
import sys
import json
import matplotlib.pyplot as plt

#-------------------------- FUNZIONI --------------------------#

# in input ci deve essere un argomento e quell'argomento deve essere una cartella
def check_args():
    if len(sys.argv) != 2:
        print("Devi passare un e solo un parametro che è il path della cartella delle misure")
        sys.exit(1)
    if not os.path.isdir(sys.argv[1]):
        print("Il parametro passato deve essere una cartella")
        sys.exit(1)

# si va a prendere i json dei valori divisi per numero di router
# crea un dizionario diverso per trilaterazione, triangolazione e ibrida
# ogni dizionario avrà come chiave il numero di router e come valore la media dell'errore per quel numero di router
def create_dicts_with_averages_per_router_cardinality():
    trilateration_dict = {}
    triangulation_dict = {}
    hybrid_dict = {}
    number_of_measures = 0

    for single_measure_folder in os.listdir(sys.argv[1]):
        single_measure_folder_path = os.path.join(sys.argv[1], single_measure_folder)
        if os.path.isdir(single_measure_folder_path):
            number_of_measures += 1
            for filename in os.listdir(single_measure_folder_path):

                if filename.endswith("trilateration_error_per_subset_dimension.json"):
                    with open(os.path.join(single_measure_folder_path, filename)) as json_file:
                        data = json.load(json_file)
                        for key in data:
                            if key not in trilateration_dict:
                                trilateration_dict[key] = 0
                            trilateration_dict[key] += data[key]

                if filename.endswith("triangulation_error_per_subset_dimension.json"):
                    with open(os.path.join(single_measure_folder_path, filename)) as json_file:
                        data = json.load(json_file)
                        for key in data:
                            if key not in triangulation_dict:
                                triangulation_dict[key] = 0
                            triangulation_dict[key] += data[key]

                if filename.endswith("mixed_algorithm_error_per_subset_dimension.json"):
                    with open(os.path.join(single_measure_folder_path, filename)) as json_file:
                        data = json.load(json_file)
                        for key in data:
                            if key not in hybrid_dict:
                                hybrid_dict[key] = 0
                            hybrid_dict[key] += data[key]
                    
    # si calcola la media per ogni numero di router
    for key in trilateration_dict:
        trilateration_dict[key] /= number_of_measures
    for key in triangulation_dict:
        triangulation_dict[key] /= number_of_measures
    for key in hybrid_dict:
        hybrid_dict[key] /= number_of_measures


    return trilateration_dict, triangulation_dict, hybrid_dict




#-------------------------- MAIN --------------------------#
if __name__ == "__main__":
