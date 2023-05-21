from tkinter import *
import scipy.io
import json
import os
import math


########## UTILITY FUNCTIONS

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
PADDING = 20*10                                #border outside the room drawing
CANVAS_WIDTH = ROOM_WIDTH + PADDING*2
CANVAS_HEIGHT = ROOM_HEIGHT + PADDING*2
TX_X = 119                                  #x position of the ap
TX_Y = 5                                    #y position of the ap
ANGLE_ERROR = 8                          #maximum +- error in the azimuth angle estimate
RX_TILT = get_param_from_json_file ("rx_tilt", "setup_localization.conf")  #how much (in degrees) the client is tilted in respect to the line that passes through the TX and the RX
DIRECTORY_BATCH_MEASURES = get_param_from_json_file("directory_batch_measures", "setup_localization.conf") #the folder containing all the measurements
NUM_MEASURES = count_directories(DIRECTORY_BATCH_MEASURES)
MAINPATH_FILE_PATH = "/processed_data/md_track/mainPathInfo.txt"



#function that gets the main path info from all the measurements
def import_main_paths_info(az_angles, el_angles, pow_values, dist_values):
    for i in range(1, NUM_MEASURES+1):
        az_angles.append(get_param_from_json_file("azimuthAngle", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH))
        el_angles.append(get_param_from_json_file("elevationAngle", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH))
        pow_values.append(get_param_from_json_file("power", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH))
        dist_values.append(get_param_from_json_file("distance", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH))

#try to estimate the client position based on the line of sight
def get_estimated_client_position(az_angles, el_angles, dist_values):
    average_distance = 0
    average_azimuth_angle = 0
    num_measurements = 0

    print("per la stima del client vado a prendere il main path delle misure ")
    for i in range(0, NUM_MEASURES):
        if((az_angles[i] + RX_TILT) in range(-ANGLE_ERROR, ANGLE_ERROR) and el_angles[i] in range(-ANGLE_ERROR, ANGLE_ERROR)): 
            print("v" + str(i+1))
            average_distance += dist_values[i]
            average_azimuth_angle += az_angles[i]
            num_measurements += 1

    #keep in mind that the distance is in meters, so i have to convert it in centimiters (*100)
    return (100 * (average_distance / num_measurements)), (average_azimuth_angle / num_measurements)

#function that draws every measure
def draw_measures(az_angles, dist_values):
    for i in range(0, NUM_MEASURES):
        #calculate the x and y coordinates of the measure
        x = TX_X + (dist_values[i]*100 * math.sin(math.radians(az_angles[i])))
        y = TX_Y + (dist_values[i]*100 * math.cos(math.radians(az_angles[i])))
        print("x: " + str(x) + " y: " + str(y) + " dist: " + str(dist_values[i]*100) + " az: " + str(az_angles[i]))

        draw_circle(myCanvas, x+PADDING, y+PADDING, 2, "orange")
        
    

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
import_main_paths_info(azimuth_angles, elevation_angles, power_values, distances)

#try to estimate the client position based on the line of sight
average_distance, average_azimuth_angle = get_estimated_client_position(azimuth_angles, elevation_angles, distances)

#canvas setup
root = Tk()
root.title("Client's aproximate position")
root.geometry(str(CANVAS_WIDTH) + "x" + str(CANVAS_HEIGHT))

myCanvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
myCanvas.pack(pady=0)


#draw room 
myCanvas.create_rectangle(0+PADDING, 0+PADDING, ROOM_WIDTH+PADDING, ROOM_HEIGHT+PADDING, fill="pink")

#draw TX
draw_circle(myCanvas, TX_X+PADDING, TX_Y+PADDING, 3, "green")

#draw RX estimated position
#draw_circle(myCanvas, TX_X+PADDING, TX_Y+average_distance+PADDING, 5, "red")

#draw measures
draw_measures(azimuth_angles, distances)

#end draw statement
root.mainloop()
