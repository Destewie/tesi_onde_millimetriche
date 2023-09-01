import os
import sys
import matplotlib.pyplot as plt

#----------------------------- FUNZIONI --------------------------------

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

    #se il dict è rimasto vuoto sollevo un'eccezione
    if not error_per_localization_method:
        raise Exception("ERROR: non ci sono file .txt nella cartella di misure")


    numero_di_misure = len(os.listdir(sys.argv[1]))

    #calcolo la media per ogni errore accumulato finora
    for(key, value) in error_per_localization_method.items():
        error_per_localization_method[key] = value/numero_di_misure

    return error_per_localization_method


def ottieni_plot(errori_medi_dict):
    
    #assegno un colore ad ogni barra
    colori = ['b', 'purple', 'r', 'c', 'm', 'y', 'k', 'w']

    plt.bar(range(len(errori_medi_dict)), list(errori_medi_dict.values()), align='center', color=colori)
    plt.xticks(range(len(errori_medi_dict)), list(errori_medi_dict.keys()))
    plt.ylabel("Errore medio (m)")
    plt.title("Errore di localizzazione medio per ogni approccio")

    return plt
    
#salva il plot nella stessa cartella passata come parametro come un pdf
def salva_plot(plot):
    nome_file = "plot_errore_medio.pdf"
    path_file = os.path.join(sys.argv[1], nome_file)
    plot.savefig(path_file, bbox_inches='tight')


#----------------------------- MAIN --------------------------------

if __name__ == "__main__":
    check_input()

    try:
        error_per_localization_method = get_average_error_per_method_from_files()
        print(error_per_localization_method)

        plot_errore_medio = ottieni_plot(error_per_localization_method)
        salva_plot(plot_errore_medio)
        plot_errore_medio.show()

    except Exception as e:
        print(e)
        exit()

