import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

#-----------------------------------FUNCTIONS----------------------------------#

# Funzione che prende in input il file json dalla path passata da linea di comando
def read_from_file(path):
    # Apro il file json
    with open(path) as json_file:
        data = json.load(json_file)

    return data

# Funzione che controlla gli argomenti passati da linea di comando
def check_args():
    # Controllo che il numero di argomenti sia corretto
    if len(sys.argv) != 2:
        print("Usage: python3 error_visualization.py <path_to_json>")
        sys.exit(1)

    return sys.argv[1]

# Funzione per salvare il plot
def save_plot(plot, file_name):
    folder_path = os.path.dirname(sys.argv[1])
    file_path = os.path.join(folder_path, file_name)
    plot.savefig(file_path)

#-------------------------------------MAIN-------------------------------------#

# Controllo gli argomenti passati da linea di comando
path = check_args()

# Leggo il file json
data = read_from_file(path)

# Creo un grafico 2D a barre con matplotlib. sulle ascisse  ci sono le key del dizionario data, sulle ordinate i valori associati alle key
plt.bar(data.keys(), data.values())
 
plt.xlabel('Number of Access Points considered')
plt.ylabel('Average error (m)')
plt.title('Average error in meters for each number of Access Points considered')

#salvo il grafico nella stessa cartella del file json
save_plot(plt, "error_visualization.png")

# Mostro il grafico
plt.show()


#-------------------------------------END--------------------------------------#
