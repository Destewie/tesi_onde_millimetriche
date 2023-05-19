from tkinter import *
import scipy.io
import json
import os

########## FUNCTIONS

#counts the number of directories (useful to know how many measurement are present in the big folder passed through the setup_localization.conf json)
def count_directories(directory):
    # Initialize the directory counter
    num_directories = 0

  # Iterate over all items in the directory
    for item in os.listdir(directory):
        # Check if the item is a directory
        if os.path.isdir(os.path.join(directory, item)):
            # Increment the directory counter
            num_directories += 1

    return num_directories

#function to get the distance from the json file that i save for each measurement
def get_param_from_json_file(parameter, file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        distance = data.get(parameter)
    return distance

#function that draws a circle given its center coordinates
def draw_circle(canvas, center_x, center_y, radius, colour):
    x1 = center_x - radius
    y1 = center_y - radius
    x2 = center_x + radius
    y2 = center_y + radius
    canvas.create_oval(x1, y1, x2, y2, fill=colour)
    
    
##########CONSTANTS (lenghts are in centimiters)
ROOM_WIDTH = 237
ROOM_HEIGHT = 428
PADDING = 20                                #border outside the room drawing
CANVAS_WIDTH = ROOM_WIDTH + PADDING*2
CANVAS_HEIGHT = ROOM_HEIGHT + PADDING*2
TX_X = 119                                  #x position of the ap
TX_Y = 5                                    #y position of the ap
AZ_ANGLE_ERROR = 8                          #maximum +- error in the azimuth angle estimate
RX_TILT = get_param_from_json_file ("rx_tilt", "setup_localization.conf")  #how much (in degrees) the client is tilted in respect to the line that passes through the TX and the RX
DIRECTORY_BATCH_MEASURES = get_param_from_json_file("directory_batch_measures", "setup_localization.conf") #the folder containing all the measurements
NUM_MEASURES = count_directories(DIRECTORY_BATCH_MEASURES)


#import matlab processed files
#todo: vatti a prendere tutte le misure presenti nella cartella che passi con il json
azAngles = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/azimuth_angles_saveFile.mat")
elAngles = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/elevation_angles_saveFile.mat")
powerValues = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/power_values_saveFile.mat")


#canvas setup
root = Tk()
root.title("Client's aproximate position")
root.geometry("500x500")

myCanvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
myCanvas.pack(pady=0)


#draw room 
myCanvas.create_rectangle(0+PADDING, 0+PADDING, ROOM_WIDTH+PADDING, ROOM_HEIGHT+PADDING, fill="pink")

#draw TX
draw_circle(myCanvas, TX_X+PADDING, TX_Y+PADDING, 3, "green")

############# prove
d = 100 * get_param_from_json_file("distance", "/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v1/processed_data/md_track/mainPathInfo.txt")
print(d)
draw_circle(myCanvas, TX_X+PADDING, TX_Y+d+PADDING, 3, "red")

#############


#end draw statement
root.mainloop()
