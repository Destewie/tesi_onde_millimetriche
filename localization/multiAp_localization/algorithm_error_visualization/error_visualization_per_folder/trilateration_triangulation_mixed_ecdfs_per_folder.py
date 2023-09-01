import os
import sys
import matplotlib.pyplot as plt

#---------------------- FUNZIONI ------------------------#

# in input ci deve essere un argomento e quell'argomento deve essere una cartella
def check_args():
    if len(sys.argv) != 2:
        print("Devi passare un e solo un parametro che è il path della cartella delle misure")
        sys.exit(1)
    if not os.path.isdir(sys.argv[1]):
        print("Il parametro passato deve essere una cartella")
        sys.exit(1)

#Funzione che prende tutti i valori dei file "trilateration_error.txt" e li mette in un array
def get_error_values():
    trilateration_error_values = []
    triangulation_error_values = []
    mixed_error_values = []

    for single_measure_dir in os.listdir(sys.argv[1]):
        full_path_measure_dir = os.path.join(sys.argv[1], single_measure_dir)
        if os.path.isdir(full_path_measure_dir):
            for file in os.listdir(full_path_measure_dir):
                if file.endswith("trilateration_error.txt"):
                    with open(os.path.join(sys.argv[1], single_measure_dir, file)) as f:
                        errore = f.readline()
                        trilateration_error_values.append(errore)
                if file.endswith("triangulation_error.txt"):
                    with open(os.path.join(sys.argv[1], single_measure_dir, file)) as f:
                        errore = f.readline()
                        triangulation_error_values.append(errore)
                if file.endswith("mixed_algorithm_error.txt"):
                    with open(os.path.join(sys.argv[1], single_measure_dir, file)) as f:
                        errore = f.readline()
                        mixed_error_values.append(errore)

    # Solleva eccezione se non ci sono file di errore
    if len(trilateration_error_values) == 0:
        raise Exception("No trilateration_error.txt files found")
    if len(triangulation_error_values) == 0:
        raise Exception("No triangulation_error.txt files found")
    if len(mixed_error_values) == 0:
        raise Exception("No mixed_algorithm_error.txt files found")
    
    return trilateration_error_values, triangulation_error_values, mixed_error_values


# Funzione che plotta i valori della ECDF
def get_ecdf_plots(error_values_trilateration, error_values_triangulation, error_values_mixed):
    error_values_trilateration.sort()
    error_values_triangulation.sort()
    error_values_mixed.sort()

    #arrotondamento al terzo decimale
    error_values_trilateration = [round(float(x), 3) for x in error_values_trilateration] 
    error_values_triangulation = [round(float(x), 3) for x in error_values_triangulation]
    error_values_mixed = [round(float(x), 3) for x in error_values_mixed] 

     
    y = []
    for i in range(len(error_values_trilateration)):
        y.append((i+1)/len(error_values_trilateration))

    #ECDF della trilaterazione colore blu
    plt.figure()
    plt.plot(error_values_trilateration, y, color='blue')
    plt.ylabel("ECDF")
    plt.xlabel("Trilateration error (m)")
    plt.title("ECDF of trilateration error")
    plt.grid(True)
    trilateration_plot = plt
    save_plot(trilateration_plot, "trilateration_error_ecdf.pdf")

    #ECDF della triangolazione colore rosso
    plt.figure()
    plt.plot(error_values_triangulation, y, color='red')
    plt.ylabel("ECDF")
    plt.xlabel("Triangulation error (m)")
    plt.title("ECDF of triangulation error")
    plt.grid(True)
    triangulation_plot = plt
    save_plot(triangulation_plot, "triangulation_error_ecdf.pdf")

    #ECDF dell'algoritmo misto colore magenta
    plt.figure()
    plt.plot(error_values_mixed, y, color='magenta')
    plt.ylabel("ECDF")
    plt.xlabel("Mixed algorithm error (m)")
    plt.title("ECDF of mixed algorithm error")
    plt.grid(True)
    mixed_plot = plt
    save_plot(mixed_plot, "mixed_algorithm_error_ecdf.pdf")

    #ECDF di tutti e tre i metodi unendo i puntini in modo diretto
    plt.figure()
    plt.plot(error_values_trilateration, y, color='blue', label="Trilateration")
    plt.plot(error_values_triangulation, y, color='red', label="Triangulation")
    plt.plot(error_values_mixed, y, color='purple', label="Mixed algorithm")
    plt.ylabel("ECDF")
    plt.xlabel("Error (m)")
    plt.title("Comparison ECDF")
    plt.legend()
    plt.grid(True)
    comparison_plot = plt
    save_plot(comparison_plot, "comparison_ecdf.pdf")


    return trilateration_plot, triangulation_plot, mixed_plot, comparison_plot


# Funzione che salva il plot come pdf nella stessa cartella passata come argomento
def save_plot(plot, file_name):
    file_path = os.path.join(sys.argv[1], file_name)
    plot.savefig(file_path, bbox_inches='tight') #bbox_inches='tight' serve per non tagliare i bordi del plot


#---------------------- MAIN ------------------------#

if __name__ == "__main__":
    check_args()

    try:
        trilateration_error_values, triangulation_error_values, mixed_error_values = get_error_values()
        trilateration_plot, triangulation_plot, mixed_plot, comparison_plot = get_ecdf_plots(trilateration_error_values, triangulation_error_values, mixed_error_values)

        trilateration_plot.show()
        triangulation_plot.show()
        mixed_plot.show()
        comparison_plot.show()

    except Exception as e:
        print(e)
        sys.exit(1)
