import puz
import numpy as np
from PIL import Image
import matplotlib
from matplotlib.pyplot import cm
import serial
from os import system
import time
import timeit


across_clues={}
down_clues = {}
mapper ={}
answersheet=[] #list of the current state of the game as per user's manipulation

"""Graphiti API Data Frames"""
all_up_frame = bytearray([0x1B,0x16,0x02])
success_frame = bytearray([0x1B,0x51])
fail_frame = bytearray([0x1B,0x52])
all_down_frame = bytearray([0x1B,0x16,0x03])
image_row_frame = bytearray([0x1B,0x18])
WriteMessage_frame = bytearray([0x1B,0x24])
gesture_frame = bytearray([0x1B,0x41,0x01])
last_touch_point_frame = bytearray([0x1B,0x44])
button_activate_frame = bytearray([0x1B,0x31,0x01])
point_status_frame = bytearray([0x1B,0x21])
point_update_frame=bytearray([0x1B,0x17])
ack_frame =bytearray([0x1B,0x51,0xAF])

# Test bytearray for display
yolo = bytearray([0x1B, 0x18, 0x06, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0xF2])

""" Constants global"""
edit_mode = 0
factor = 2
tempframe=bytearray([])
top_buffer=2
side_buffer=2

p = puz.read('one.puz')
ser = serial.Serial("/dev/tty.usbmodem141101", baudrate="115200",timeout=0.001)

numbering = p.clue_numbering()
temp =np.empty([len(p.fill)])
Matrix = np.array( [[0 for x in range(p.width)] for y in range(p.height)])

"""------------------- GRAPHITI INITIALIZATION FUNCTIONS ----------------------------"""
def UpdateScreen (Frame):
    """
    Parameters: Frame- Bytearray of the API command, without the checksum
    Return: prints out [] if success, [ <text> ] if fail
    Function to send data to Graphiti with any particular specified frame. This function automatically adds the checksum
    """
    ### TODO: Rename this to something Better, even in the other Graphoto file
    
    checksum = sum(Frame) #adding software checksum
    Frame.extend((checksum // 256, checksum % 256))
    ser.write(Frame)
    response = ser.readlines()
    response_list = list(response)
    time.sleep(0.01)
## Could be removed :
##    success_list = list(str(success_frame))
##    success_check = success_list[0]+success_list[1]+success_list[2]+success_list[3]

    
def RefreshScreen():
    """
    Refreshes the graphiti screen by raising and loweing all pins.
    """
    UpdateScreen(all_down_frame)
    UpdateScreen(success_frame)

def Img2Screen (img):
    global factor,tempframe
    counter = top_buffer
    if(factor!=1):
        img = np.repeat(np.repeat(img,factor, axis=0), factor, axis=1)

##    ##TOP LINE HArdcoded
    row_frame = image_row_frame + bytearray([chr(counter)])
    for x in range (0,side_buffer-1):
        row_frame = row_frame + bytearray([0x00,0x00])
    for x in range(0,len(img)+top_buffer+2):
        row_frame = row_frame +bytearray([chr(4),0x00])
    while (len(row_frame)<=123):
            row_frame = row_frame + bytearray([0x00,0x00])
    time.sleep(0.1)
    UpdateScreen(row_frame)
    print "top line"
    counter+=1
    row_frame = image_row_frame + bytearray([chr(counter)])
    for x in range (0,side_buffer-1):
        row_frame = row_frame + bytearray([0x00,0x00])
    row_frame = row_frame +bytearray([0x04,0x00])
    for x in range(0,len(img)+top_buffer):
        row_frame = row_frame +bytearray([chr(0),0x00])
    row_frame = row_frame +bytearray([0x04,0x00])
    while (len(row_frame)<=123):
            row_frame = row_frame + bytearray([0x00,0x00])
    UpdateScreen(row_frame)
    print "bottomlinse"
    counter+=1
    
    

##        ##TOP LINE HArdcoded
##    row_frame = image_row_frame + bytearray([chr(counter)])
##    for x in range (0,side_buffer-1):
##        row_frame = row_frame + bytearray([0x00,0x00])
##    for x in range(0,len(img)+2):
##        print "line"
##        row_frame = row_frame +bytearray([chr(4),0x00])
##    while (len(row_frame)<=123):
##            row_frame = row_frame + bytearray([0x00,0x00])
##    UpdateScreen(row_frame)
                            

    print"updated"
    ##BOTTOM LINE HARDCODED
    row_frame = image_row_frame + bytearray([chr(len(img)+top_buffer+2)])
    for x in range (0,side_buffer-1):
        row_frame = row_frame + bytearray([0x00,0x00])
    for y in range(0,len(img)+top_buffer+2):
        row_frame = row_frame +bytearray([0x04,0x00])
    while (len(row_frame)<=123):
            row_frame = row_frame + bytearray([0x00,0x00])
    UpdateScreen(row_frame)

    row_frame = image_row_frame + bytearray([chr(len(img)+top_buffer+1)])
    for x in range (0,side_buffer-1):
        row_frame = row_frame + bytearray([0x00,0x00])
    row_frame = row_frame +bytearray([0x04,0x00])
    for x in range(0,len(img)+top_buffer):
        row_frame = row_frame +bytearray([chr(0),0x00])
    row_frame = row_frame +bytearray([0x04,0x00])
    while (len(row_frame)<=123):
            row_frame = row_frame + bytearray([0x00,0x00])

    UpdateScreen(row_frame)
    

    
    while(counter<len(img)+top_buffer):
        print counter
        row_frame = image_row_frame + bytearray([chr(counter+1)])
        if(counter == 26):
            print "Exception line"
            row_frame = row_frame +bytearray([0X1B])
        for x in range (0,side_buffer-1):
            row_frame = row_frame + bytearray([0x00,0x00])
        row_frame = row_frame + bytearray([0x04,0x00,0x00,0x00])
##        print list(img[counter-top_buffer])
        try:
            for element in list(img[counter-top_buffer]):
                #print element[0]
                if (element[0] >0.2):
                    row_frame = row_frame +bytearray([chr(1),0x00])
                else:
                    row_frame = row_frame +bytearray([chr(4),0x00])
        except:
            print "there it crashed for"+ str(counter)
            for element in list(img[counter-top_buffer-1]):
                #print element[0]
                if (element[0] >0.2):
                    row_frame = row_frame +bytearray([chr(1),0x00])
                else:
                    row_frame = row_frame +bytearray([chr(4),0x00])
        print len(row_frame)
        row_frame = row_frame + bytearray([0x00,0x00,0x04,0x00])
        while (len(row_frame)<=123):
            row_frame = row_frame + bytearray([0x00,0x00])
        print len(row_frame)
        counter +=1
        UpdateScreen(row_frame)
##        list(img[counter-top_buffer+1])
        print " -------"
    

def PrintImg(img):
    RefreshScreen()
    Img2Screen(img)

def InitialSetup(img):
    PrintImg(img)

"""-------------------- CROSSWORD INITIALIZATION FUCTIONS -----------------------------"""
def GenerateImage():
    """
    Initialization Step 1
    This function creates a black and white image of the crossword out of the data from the .puz file.
    A dash(-) corresponds to an open space, while a dot(.) corrosponds to a closed space on the crossword.
    """
    global Matrix,temp,p
    print Matrix
    print temp
    for row in range(len(p.fill)):
        if (p.fill[row] == '-'):
            temp[row] = (1)
        else:
            temp[row] = (0)
    MapCellsToMatrix()
    matplotlib.image.imsave('crossword.png', Matrix, cmap=cm.gray)

    
def MapCellsToMatrix():
    """
    Initialization Step 2
    This function creates a map between the cells as the data is stored in .puz and matrix grid, as the interaction happens with the graphiti device.
    The dictionary is called mapper, and is in the format = {cell:(x,y)}
    """
    count = 0
    global Matrix,temp,p
    for row in range(p.height):
        for element in range(p.width):
            #print (count)
            Matrix[row][element] = int(temp[count])
            mapper[count] = (row+1,element+1)
            count +=1

            
def GenerateClues():
    """
    Initialization Step 3
    Generate across and down clues from the data, and store it in the form of a dictionary {cell:"the clue is ....... of length ...."}
    """
    for element in numbering.across:
        across_clues[element['cell']]= "The Across clue is . . . "+str(element['clue'].encode('utf-8'))+", and is of a total length of "+str(element['len'])
    for element in numbering.down:
        down_clues[element['cell']]= "The Down clue is . . .  "+str(element['clue'].encode('utf-8'))+", and is of a total length of "+str(element['len'])

def GenerateAnswerSheet():
    """
    Initialization Step 4
    Generate an answersheet that the user can refer back to as per required
    """
    global answersheet
    for element in Matrix:
        entry = []
        for piece in element:
            if (piece == 1):
                value = 'Empty'
            if (piece == 0):
                value = 'Closed Box'

            entry.append(value)
        answersheet.append(entry)


"""-------------------- INTERACTION FUCTIONS -----------------------------"""
def GetCellFromCoord(x,y):
    """
    Function
    Parameters: x,y coordinate on the matrix
    Return: Cell number
    
    This function returns a cell number corrosponding to the x,y coordinate on the crossword.
    """
    x = x
    y = y
    for element in mapper:
        if (mapper[element] ==(x,y)):
            return element

def SpeakClue(direction,x,y):

    global current_direction
    """
    Function
    Parameters: Direction (A for across and D for down), x and y coordinates on the crossword.
    Return: Clue in the form of a string

    This function returns a string of clue that can be announced by system for any direction specified
    """
    ### TODO: Smoothen this function, so that if the touch is on a closed spot, it says so.
    ### TODO: Smoothen this function so that if the touch is on a spot that is not a start of the sentence, it specifies that.
    ### TODO: Smoothen this function, so that if the the point has an across hint, and user asks for down, it mentions that, and asks user to click the down button instead... good idea?
    xclue = x
    yclue = y
    print (x,y)
    print GetCellFromCoord(xclue,yclue)
    if (direction == "A"):
        print "Across"
        try :
            print"Tried"
            clue = across_clues[GetCellFromCoord(xclue,yclue)]
            current_direction = direction
            print "here we go"
            system("Say 'Point"+str(x)+"comma"+str(y)+" .........'" )
            system("Say 'The"+ clue+" .'")
            print"the end"
        except:
            system("Say 'Point"+str(x)+"comma"+str(y)+" does not have a word running across.'")
    elif (direction == "D"):
        try:
            clue = down_clues[GetCellFromCoord(xclue,yclue)]
            current_direction = direction
            system("Say 'For the point"+str(x)+"comma "+str(y)+"........... '")
            system("Say '"+clue+" .'")
        except:
            system("Say 'Point"+str(x)+"comma"+str(y)+" does not have a word running down.'")
            
        
    else:
        print "Error specifying the driection!!!!!"

def Edit(x,y):
    """
    
    """
    if (current_direction == "A"):
        if(GetCellFromCoord(x,y) in across_clues):
            print "WRITE ACROSS BRO!"
        else:
            print "You cant edit this work in the across mode"
    elif (current_direction == "D"):
        if(GetCellFromCoord(x,y) in down_clues):
            print "Write down BRO!"
        else:
            print "You cant edit this work in the down mode"

            
    

def SpeakButton(x,y):
    """
    Function
    Decides what is to be spoken, if it should be the text, or say empty if it is empty.
    """
    if(answersheet[x][y] == 'Blank'):
        print "Speak BLANK!"
    elif(answersheet[x][y] == 'Closed'):
        print "SPeak Closed!"
    else:
        print "speak"+ answersheet[x][y]
        
    
    
    pass

def GetLocation(response):
    ##TODO: ASK KEN HOW WOULD THIS TOUCH THING WORK EXACTLY? EXPLAIN OUR LOGIC ABOUT THE THING< AND ASK FOR THE BEST THING WE CAN 
    row = ord(list(response)[2])
    column = ord(list(response)[3])
    return((row-top_buffer)/factor,(column-side_buffer)/factor+1)

def AnnounceContent(row,column):

    ##TODO: Button to repeat a clue?
    ## TODO: Repeat a clue?
    ## TODO: Announce clues differently?
    yolo=False
    print (row,column)
    if(row<=15 and column<=15):
        point_height_frame = point_status_frame + bytearray(chr(row+top_buffer)) + bytearray(chr(column+side_buffer))
        UpdateScreen(point_height_frame)
        height_response = ser.readline()
        while (height_response == None or len(list(height_response)) != 6):
            height_response = ser.readline()
        if(list(height_response)[2]==chr(row+top_buffer) and list(height_response)[3]==chr(column+side_buffer)):
            height_response =  ord(list(height_response)[4])
            point_notify1 = point_update_frame +bytearray([((row*factor)+top_buffer),((column*factor)+side_buffer),4,0x04])
##            point_notify2 = point_update_frame +bytearray([((row*factor)+top_buffer)-1,((column*factor)+side_buffer),4,0x04])
##            point_notify3 = point_update_frame +bytearray([((row*factor)+top_buffer),((column*factor)+side_buffer)-1,4,0x04])
##            point_notify4 = point_update_frame +bytearray([((row*factor)+top_buffer)-1,((column*factor)+side_buffer)-1,4,0x04])
            UpdateScreen(point_notify1)
            time.sleep(0.01)
##            UpdateScreen(point_notify2)
##            time.sleep(0.01)
##            UpdateScreen(point_notify3)
##            time.sleep(0.01)
##            UpdateScreen(point_notify4)
            
            point_notify1 = point_update_frame +bytearray([((row*factor)+top_buffer),((column*factor)+side_buffer),height_response,0x00])
##            point_notify2 = point_update_frame +bytearray([((row*factor)+top_buffer)-1,((column*factor)+side_buffer),height_response,0x00])
##            point_notify3 = point_update_frame +bytearray([((row*factor)+top_buffer),((column*factor)+side_buffer)-1,height_response,0x00])
##            point_notify4 = point_update_frame +bytearray([((row*factor)+top_buffer)-1,((column*factor)+side_buffer)-1,height_response,0x00])
            yolo = True
        system("Say 'Point"+str(row)+"comma"+str(column)+" .'" )
        system("Say 'Character stored is"+answersheet[row-1][column-1]+" .'")
        if(yolo):
            UpdateScreen(point_notify1)
            time.sleep(0.01)
##            UpdateScreen(point_notify2)
##            time.sleep(0.01)
##            UpdateScreen(point_notify3)
##            time.sleep(0.01)
##            UpdateScreen(point_notify4)
##            time.sleep(0.01)
##            yolo = False
        
        
    print "!!!"
    print "___________________________"

    
def GetLastTouch():
    UpdateScreen(last_touch_point_frame)
    response = ser.readline()
    while (response == None or len(list(response)) != 6 ):
        response = (ser.readline())
    return response




def EditContent():
    pass






## Printing all the clues in the puzzle       
print 'Across'
for clue in numbering.across:
    answer = ''.join(p.solution[clue['cell'] + i]for i in range(clue['len']))
    print clue['num'], clue['clue'], '-', answer

print 'Down'
for clue in numbering.down:
    answer = ''.join(p.solution[clue['cell'] + i * numbering.width]for i in range(clue['len']))
    print clue['num'], clue['clue'], '-', answer


## Prints the grid of the puzzle
for row in range(p.height):
    cell = row * p.width
    # Substitute p.solution for p.fill to print the answers
    print ' '.join(p.solution[cell:cell + p.width])
			
GenerateImage()
##MapCellsToMatrix()
GenerateClues()
GenerateAnswerSheet()

print "starting up ..."
#Initialize the Graphiti
RefreshScreen

img = matplotlib.image.imread('crossword.png')
InitialSetup(img) #puzzle displayed for the first time
UpdateScreen(button_activate_frame)

while ser.is_open:
    response_button = ser.readline()
    button_value = list(response_button)
    rest = GetLastTouch
##    print button_value
    if (len(list(response_button)) > 0 and (button_value[1]) == "2") :
##        print (ord(button_value[3]),ord(button_value[4]))
        
        if (ord(button_value[4])==2 and ord(button_value[3])==2):
            print "space yo"
            answer= (0,0)
            start = timeit.timeit()
            response = GetLastTouch()
            answer = GetLocation(response)
            if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32): 
                AnnounceContent(answer[0],answer[1])
           
            
        if( ord(button_value[3]) ==128 and ord(button_value[4]) ==2):
            print "right yo"
            response = GetLastTouch()
            answer = GetLocation(response)
            print answer
            if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32): 
                SpeakClue("A",answer[0],answer[1])
            else:
                system("Say 'Try again'")
            
        if( ord(button_value[3]) ==32 and ord(button_value[4]) ==2):
            print "left yo"
            TryRight()
        if( ord(button_value[3]) ==64 and ord(button_value[4]) ==2):
            print "down yo"
            response = GetLastTouch()
            answer = GetLocation(response)
            if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32): 
                SpeakClue("D",answer[0],answer[1])
           
        if( ord(button_value[3]) ==16 and ord(button_value[4]) ==2):
            print "up yo"
            TryDown()
        if( ord(button_value[3]) ==1 and ord(button_value[4]) ==2):
            print "select yo"
            response = GetLastTouch()
            EditContent(response)
        UpdateScreen(ack_frame)


[]
[]


