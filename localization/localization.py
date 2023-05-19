from tkinter import *

#CONSTANTS
ROOM_WIDTH = 237
ROOM_HEIGHT = 428
PADDING = 20
CANVAS_WIDTH = ROOM_WIDTH + PADDING*2
CANVAS_HEIGHT = ROOM_HEIGHT + PADDING*2
TX_X = 119
TX_Y = 15

#function that draws a circle given its center coordinates
def draw_circle(canvas, center_x, center_y, radius, colour):
    x1 = center_x - radius
    y1 = center_y - radius
    x2 = center_x + radius
    y2 = center_y + radius
    canvas.create_oval(x1, y1, x2, y2, fill=colour)

#canvas setup
root = Tk()
root.title("Client's aproximate position")
root.geometry("500x500")

myCanvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
myCanvas.pack(pady=0)


#draw room 
myCanvas.create_rectangle(0+PADDING, 0+PADDING, ROOM_WIDTH+PADDING, ROOM_HEIGHT+PADDING, fill="pink")

#draw TX
draw_circle(myCanvas, TX_X+PADDING, TX_Y+PADDING, 3, "red")




#end draw statement
root.mainloop()
