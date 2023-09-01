import os
import sys

#-------------------------------------------------------------

# Funzione che controlla che ci sia un parametro in ingresso e che questo sia una cartella
def check_input():
    if len(sys.argv) != 2:
        print("ERROR: devi inserire il path della cartella di misure")
        exit()
    if not os.path.isdir(sys.argv[1]):
        print("ERROR: il parametro inserito non è una cartella")
        exit()

#Funzione che va a prendere il valore contenuto in tutti i file .txt presenti nella cartella di misure e crea la media per ogni metodo di localizzazione
def get_average_error_per_method_from_files():
    error_per_localization_method = {}

    for dir_misura in os.listdir(sys.argv[1]):
        full_path_dir_misura = os.path.join(sys.argv[1], dir_misura)
        if(os.path.isdir(full_path_dir_misura)):
            for file in os.listdir(full_path_dir_misura):
                if file.endswith(".txt"):
                    #prendo la parte prima del .txt e, se non esiste, la creo con valore 0
                    #se esiste, aggiungo il valore del file
                    nome_file = file.split(".")[0]
                    valore_nel_dizionario = error_per_localization_method.get(nome_file, 0) #se il metodo non esiste, ritorna 0
                    path_file_errore = os.path.join(sys.argv[1], dir_misura, file)
                    errore_da_file = float(open(path_file_errore, "r").read())
                    error_per_localization_method[nome_file] = valore_nel_dizionario + errore_da_file

    numero_di_misure = len(os.listdir(sys.argv[1]))

    #calcolo la media per ogni errore accumulato finora
    for(key, value) in error_per_localization_method.items():
        error_per_localization_method[key] = value/numero_di_misure

    return error_per_localization_method

#-------------------------------------------------------------

if __name__ == "__main__":
    check_input()
    error_per_localization_method = get_average_error_per_method_from_files()
    print(error_per_localization_method)


