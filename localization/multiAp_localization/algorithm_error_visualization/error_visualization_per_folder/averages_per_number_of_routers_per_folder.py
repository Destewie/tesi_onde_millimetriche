import os
import sys
import json
import numpy as np
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


# Plotta dei grafici a colonne con i valori medi dell'errore per ogni numero di router 

def plot_graphs(trilateration_dict, triangulation_dict, hybrid_dict):
    # si ordinano i dizionari per numero di router
    trilateration_dict = dict(sorted(trilateration_dict.items()))
    triangulation_dict = dict(sorted(triangulation_dict.items()))
    hybrid_dict = dict(sorted(hybrid_dict.items()))

    # si creano le liste con i valori dei dizionari
    trilateration_values = list(trilateration_dict.values())
    triangulation_values = list(triangulation_dict.values())
    hybrid_values = list(hybrid_dict.values())

    # si creano le liste con le chiavi dei dizionari
    trilateration_keys = list(trilateration_dict.keys())
    triangulation_keys = list(triangulation_dict.keys())
    hybrid_keys = list(hybrid_dict.keys())

    # si crea il plot a colonne per la trilaterazione
    plt.figure()
    plt.bar(trilateration_keys, trilateration_values, color='blue')
    plt.xlabel("Number of anchors")
    plt.ylabel("Average error (m)")
    plt.title("Trilateration average error per number of anchors")
    salva_plot(plt, "trilateration_average_error_per_number_of_routers.pdf")

    # si crea il plot a colonne per la triangolazione
    plt.figure()
    plt.bar(triangulation_keys, triangulation_values, color='red')
    plt.xlabel("Number of anchors")
    plt.ylabel("Average error (m)")
    plt.title("Triangulation average error per number of anchors")
    salva_plot(plt, "triangulation_average_error_per_number_of_routers.pdf")

    # si crea il plot a colonne per l'algoritmo ibrido
    plt.figure()
    plt.bar(hybrid_keys, hybrid_values, color='purple')
    plt.xlabel("Number of anchors")
    plt.ylabel("Average error (m)")
    plt.title("Hybrid algorithm average error per number of anchors")
    salva_plot(plt, "hybrid_algorithm_average_error_per_number_of_routers.pdf")


#salva il plot nella stessa cartella passata come parametro come un pdf
def salva_plot(plot, nome_file):
    path_file = os.path.join(sys.argv[1], nome_file)
    plot.savefig(path_file, bbox_inches='tight')



#-------------------------- MAIN --------------------------#
if __name__ == "__main__":
    check_args()

    trilateration_dict, triangulation_dict, hybrid_dict = create_dicts_with_averages_per_router_cardinality()
    
    plot_graphs(trilateration_dict, triangulation_dict, hybrid_dict)

    #prova plot generale con tutti i valori
    plt.figure()
    #mi faccio una lista con tutte le chiavi dei dizionari
    keys = list(hybrid_dict.keys())
    #mi faccio dei vettori con i valori dei dizionari per ogni chiave
    hybrid_values = []
    trilateration_values = []
    triangulation_values = []
    for key in keys:
        hybrid_values.append(hybrid_dict.get(key, 0))
        trilateration_values.append(trilateration_dict.get(key, 0))
        triangulation_values.append(triangulation_dict.get(key, 0))

    x_axis = np.arange(len(keys))

    plt.bar(x_axis-0.2, triangulation_values, width=0.2, color='red', label="Triangulation error")
    plt.bar(x_axis+0.2, trilateration_values, width=0.2, color='blue', label="Trilateration error")
    plt.bar(x_axis, hybrid_values, width=0.2, color='purple', label="Hybrid algorithm error")

    plt.xticks(x_axis, keys)
    plt.xlabel("Number of anchors")
    plt.ylabel("Average error (m)")
    plt.title("Average error per number of anchors")
    plt.legend()
    salva_plot(plt, "average_error_per_number_of_routers.pdf")
    plt.show()
    
    



