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
        result = data.get(parameter)
    return result

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
ANGLE_ERROR = 8                          #maximum +- error in the azimuth angle estimate
RX_TILT = get_param_from_json_file ("rx_tilt", "/home/des/Documents/università/tesi_onde_millimetriche/localization/setup_localization.conf")  #how much (in degrees) the client is tilted in respect to the line that passes through the TX and the RX
DIRECTORY_BATCH_MEASURES = get_param_from_json_file("directory_batch_measures", "setup_localization.conf") #the folder containing all the measurements
NUM_MEASURES = count_directories(DIRECTORY_BATCH_MEASURES)


#import matlab processed files
#servirà in futuro, quando dovrò guardare dati oltre al main path per ogni misura
azAngles = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/azimuth_angles_saveFile.mat")
elAngles = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/elevation_angles_saveFile.mat")
powerValues = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/power_values_saveFile.mat")


#import all main path info from all the folders in #DIRECTORY_BATCH_MEASURES
azimuth_angles = []
elevation_angles = []
power_values = []
distances = []
for i in range(1, NUM_MEASURES+1):
    azimuth_angles.append(get_param_from_json_file("azimuthAngle", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + "/processed_data/md_track/mainPathInfo.txt"))
    elevation_angles.append(get_param_from_json_file("elevationAngle", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + "/processed_data/md_track/mainPathInfo.txt"))
    power_values.append(get_param_from_json_file("power", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + "/processed_data/md_track/mainPathInfo.txt"))
    distances.append(get_param_from_json_file("distance", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + "/processed_data/md_track/mainPathInfo.txt"))

#try to estimate the client position based on the line of sight
average_distance = 0
average_azimuth_angle = 0
num_measurements = 0
print("per la stima del client vado a prendere il main path delle misure ")
for i in range(0, NUM_MEASURES):
    if((azimuth_angles[i] + RX_TILT) in range(-ANGLE_ERROR, ANGLE_ERROR) and elevation_angles[i] in range(-ANGLE_ERROR, ANGLE_ERROR)):        
        print("v" + str(i+1))
        average_distance += distances[i]
        average_azimuth_angle += azimuth_angles[i]
        num_measurements += 1
average_distance = 100 * (average_distance / num_measurements)
average_azimuth_angle = average_azimuth_angle / num_measurements


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

#draw RX estimated position
draw_circle(myCanvas, TX_X+PADDING, TX_Y+average_distance+PADDING, 5, "red")


#end draw statement
root.mainloop()
