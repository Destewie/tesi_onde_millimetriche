import os
import sys
import matplotlib.pyplot as plt

#---------------------- FUNZIONI ------------------------#

# in input ci deve essere un argomento e quell'argomento deve essere una cartella
def check_args():
    if len(sys.argv) != 2:
        print("Usage: python3 trilateration_error_ecdf_per_folder.py <folder>")
        sys.exit(1)
    if not os.path.isdir(sys.argv[1]):
        print("Usage: python3 trilateration_error_ecdf_per_folder.py <folder>")
        sys.exit(1)

#Funzione che prende tutti i valori dei file "trilateration_error.txt" e li mette in un array
def get_trilateration_error_values():
    trilateration_error_values = []

    for single_measure_dir in os.listdir(sys.argv[1]):
        full_path_measure_dir = os.path.join(sys.argv[1], single_measure_dir)
        if os.path.isdir(full_path_measure_dir):
            for file in os.listdir(full_path_measure_dir):
                if file.endswith("trilateration_error.txt"):
                    with open(os.path.join(sys.argv[1], single_measure_dir, file)) as f:
                        errore = f.readline()
                        trilateration_error_values.append(errore)

    # Solleva eccezione se non ci sono file "trilateration_error.txt"
    if len(trilateration_error_values) == 0:
        raise Exception("No trilateration_error.txt files found")

    return trilateration_error_values


# Funzione che plotta i valori della ECDF
def get_plot_ecdf(error_values):
    error_values.sort()
    error_values = [round(float(x), 3) for x in error_values] # arrotonda al terzo decimale
     
    y = []
    for i in range(len(error_values)):
        y.append((i+1)/len(error_values))

    # Plot della ECDF colore blu
    plt.figure()
    plt.step(error_values, y, color='blue')
    plt.ylabel("ECDF")
    plt.xlabel("Trilateration error (m)")
    plt.title("ECDF of trilateration error")
    plt.grid(True)

    return plt


# Funzione che salva il plot come pdf nella stessa cartella passata come argomento
def save_plot(plot):
    name = "trilateration_error_ecdf.pdf"
    file_path = os.path.join(sys.argv[1], name)
    plot.savefig(file_path, bbox_inches='tight') #bbox_inches='tight' serve per non tagliare i bordi del plot


#---------------------- MAIN ------------------------#

if __name__ == "__main__":
    check_args()

    try:
        trilateration_error_values = get_trilateration_error_values()

        plot = get_plot_ecdf(trilateration_error_values)
        save_plot(plot)
        plot.show()

    except Exception as e:
        print(e)
        sys.exit(1)
