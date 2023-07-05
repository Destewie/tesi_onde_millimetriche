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
ROOM_WIDTH = get_param_from_json_file("room_width", "setup_localization.conf")
ROOM_HEIGHT = get_param_from_json_file("room_height", "setup_localization.conf")
PADDING = 20*10                             #border outside the room drawing
CANVAS_WIDTH = ROOM_WIDTH + PADDING*2
CANVAS_HEIGHT = ROOM_HEIGHT + PADDING*2
TX_X = get_param_from_json_file("tx_x", "setup_localization.conf")  #x position of the ap
TX_Y = get_param_from_json_file("tx_y", "setup_localization.conf")  #y position of the ap
RX_X = get_param_from_json_file("rx_x", "setup_localization.conf")  #x position of the client
RX_Y = get_param_from_json_file("rx_y", "setup_localization.conf")  #y position of the client
ANGLE_ERROR = 7                             #maximum +- error in the azimuth angle estimate
DISTANCE_PERCENTAGE_ERROR = 1.5             #maximum +- error in the distance estimate
RX_TILT = get_param_from_json_file ("rx_tilt", "setup_localization.conf")  #how much (in degrees) the client is tilted in respect to the line that passes through the TX and the RX
DIRECTORY_BATCH_MEASURES = get_param_from_json_file("directory_batch_measures", "setup_localization.conf") #the folder containing all the measurements
NUM_MEASURES = count_directories(DIRECTORY_BATCH_MEASURES)
MAINPATH_FILE_PATH = "/processed_data/md_track/mainPathInfo.txt"

possible_angles = range(-ANGLE_ERROR, ANGLE_ERROR)


class Measure:
    #angles are in degrees, distance is in centimiters
    def __init__(self, id, azimuthAngle, elevationAngle, power, distance):
        self.id = id
        self.azimuthAngle = azimuthAngle
        self.elevationAngle = elevationAngle
        self.power = power
        self.distance = distance * 100
        #calculate the x and y coordinates of the measure
        self.x, self.y = convert_azimuth_to_canvas_coordinates(self.distance, self.azimuthAngle)

    def draw(self):
        draw_circle(myCanvas, self.x+PADDING, self.y+PADDING, 2, "orange")

    def getName(self):
        return "v" + str(self.id)

    def printSpecs(self):
        print("name: " + self.getName())
        print("azimuth angle: " + str(self.azimuthAngle))
        print("elevation angle: " + str(self.elevationAngle))
        print("power: " + str(self.power))
        print("distance: " + str(self.distance))
        print("x: " + str(self.x))
        print("y: " + str(self.y))
        print("")

#a group of measures that have similar caracteristics (similar distance and azimuth angle)
#class Group:
#    def __init__(self, measures) -> None:
#        self.measures = measures




#function that gets the main path info from all the measurements
def import_measures():
    measures_array = []
    for i in range(1, NUM_MEASURES+1):
        azimuth_angle = get_param_from_json_file("azimuthAngle", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH)
        elevation_angle = get_param_from_json_file("elevationAngle", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH)
        power = get_param_from_json_file("power", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH)
        distance = get_param_from_json_file("distance", DIRECTORY_BATCH_MEASURES + "/v" + str(i) + MAINPATH_FILE_PATH)
        measures_array.append( Measure(i, azimuth_angle, elevation_angle, power, distance) )

    return measures_array

#try to estimate the client position based on the line of sight
def get_estimated_client_position(measures):
    average_distance = 0
    average_azimuth_angle = 0
    num_measurements = 0

    print("per la stima del client vado a prendere il main path delle misure ")
    for i in range(0, NUM_MEASURES):
        if(distance_percentage_diff(measures[0], measures[i]) < DISTANCE_PERCENTAGE_ERROR and (measures[i].azimuthAngle + RX_TILT) in possible_angles and measures[i].elevationAngle in possible_angles): 
            print(measures[i].getName())
            average_distance += measures[i].distance
            average_azimuth_angle += measures[i].azimuthAngle
            num_measurements += 1


    #keep in mind that the distance is in meters, so i have to convert it in centimiters (*100)
    return (average_distance / num_measurements), (average_azimuth_angle / num_measurements)

#function that uses TX coordinates, distance from TX to RX and the azimuth angle to calculate the coordinates of the RX
def convert_azimuth_to_canvas_coordinates(distance, azimuth_angle):
    x = TX_X + (distance * math.sin(math.radians(azimuth_angle)))
    y = TX_Y + (distance * math.cos(math.radians(azimuth_angle)))
    return x, y

#prints all the percentage difference in distance between the first measure and the others
def percentage_diff_in_distance(measures):
    print("percentage difference in distance between the measure with least distance from the TX and the others:")
    first_measure = measures[0]
    for i in range(1, NUM_MEASURES):
        print(measures[i].getName() + ": " + str(100 * (measures[i].distance - first_measure.distance) / first_measure.distance) + "%")
    print("")


#calculates the percentage difference in distance between two measures
def distance_percentage_diff(measure1, measure2):
    return int(100 * (measure2.distance - measure1.distance) / measure1.distance)
    
#creates groups based on the distance_percentage_diff. The groups are created by taking the first measure and comparing it with the others. when a measure has the difference > DISTANCE_PERCENTAGE_ERROR becomes the leader of the group and the following measures are based on it.
def create_groups(measures):
    groups = []
    group = []
    leader_measure = measures[0]
    group.append(leader_measure)
    for i in range(1, NUM_MEASURES):
        #if the distance percentage difference is less than the error and their azimuth angle is kinda close, put it in the group
        if(distance_percentage_diff(leader_measure, measures[i]) < DISTANCE_PERCENTAGE_ERROR and ((leader_measure.azimuthAngle - measures[i].azimuthAngle) in possible_angles)) :
            group.append(measures[i])
        else:
            leader_measure = measures[i]
            groups.append(group)
            group = []
            group.append(measures[i])
    groups.append(group)
    return groups

#print groups
def print_groups(groups):
    i=0
    for group in groups:
        print("group:" + str(i))
        i+=1
        for measure in group:
            print(measure.getName())

        print("")

#draw every group as an average of every member of the group
def draw_groups(groups):
    for group in groups:
        average_x = 0
        average_y = 0
        for measure in group:
            average_x += measure.x
            average_y += measure.y
        average_x = average_x / len(group)
        average_y = average_y / len(group)
        draw_circle(myCanvas, average_x+PADDING, average_y+PADDING, 5, "orange")


#get wall estimations
#a wall is in between the RX estimate and the average of every member of the group 
def draw_wall_estimations(groups, client_x, client_y):
    for group in groups:
        average_x = 0
        average_y = 0
        for measure in group:
            average_x += measure.x
            average_y += measure.y
        average_x = average_x / len(group)
        average_y = average_y / len(group)

        #now the position of the wall is the average between client x and y positions
        wall_x = (client_x + average_x) / 2
        wall_y = (client_y + average_y) / 2
        draw_circle(myCanvas, wall_x+PADDING, wall_y+PADDING, 3, "blue")





#import matlab processed files
#servirà in futuro, quando dovrò guardare dati oltre al main path per ogni misura
#azAngles = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/azimuth_angles_saveFile.mat")
#elAngles = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/elevation_angles_saveFile.mat")
#powerValues = scipy.io.loadmat("/home/des/Documents/università/tesi_onde_millimetriche/MikroTik-mD-Track/Example_data/2023-05-18_measurements/v11/processed_data/md_track/power_values_saveFile.mat")


#import all main path info from all the folders in #DIRECTORY_BATCH_MEASURES
measures = import_measures()

#sort the measures by distance from the TX
measures.sort(key=lambda x: x.distance)

#print the percentage difference in distance between the first measure and the others
percentage_diff_in_distance(measures)

#print the groups
groups = print_groups(create_groups(measures))

#print the specs of the measures
#for i in range(0, NUM_MEASURES):
#    measures[i].printSpecs()


############################################################################################## DRAWING

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

#draw RX
draw_circle(myCanvas, RX_X+PADDING, RX_Y+PADDING, 3, "green")

#draw groups
draw_groups(create_groups(measures))

#draw RX estimated position
estimatedDist, estimatedAz = get_estimated_client_position(measures)
rx_x, rx_y = convert_azimuth_to_canvas_coordinates(estimatedDist, estimatedAz)
draw_circle(myCanvas, rx_x+PADDING, rx_y+PADDING, 6, "red")

#draw wall estimations
draw_wall_estimations(create_groups(measures), rx_x, rx_y)

#draw every single measure
for i in range(0, NUM_MEASURES):
    measures[i].draw()

#end draw statement
root.mainloop()

############################################################################################## END DRAWING

