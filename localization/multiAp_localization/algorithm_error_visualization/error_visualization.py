import json
import matplotlib.pyplot as plt
import numpy as np
import sys

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

# Mostro il grafico
plt.show()

#-------------------------------------END--------------------------------------#
