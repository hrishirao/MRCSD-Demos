import puz
import numpy as np
from PIL import Image
import matplotlib
from matplotlib.pyplot import cm
import serial
from os import system
import time
import timeit
import sys,linecache


"""--------------------------------------------Graphiti API Data Frames------------------------------------------------------"""
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
#Character dict for the keyboard
characterdict ={(16,0):'a',(48,0):'b',(17,0):'c',(19,0):'d',(18,0):'e',(49,0):'f',(51,0):'g',(50,0):'h',(33,0):'i',(35,0):'j',(80,0):'k',(112,0):'l',(81,0):'m',(83,0):'n',(82,0):'o',(113,0):'p',(115,0):'q',(114,0):'r',(97,0):'s',(99,0):'t',(84,0):'u',(116,0):'v',(39,0):'w',(85,0):'x',(87,0):'y',(86,0):'z',(128,0):'backspace'}
# Test bytearray for raising 6th row to height 4
yolo = bytearray([0x1B, 0x18, 0x06, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0xF2])

"""----------------------------------- Constants global---------------------------------------------------------"""
edit_mode = 0
edit_mode_char_len = 0
cursor_live = 0
charcount = 1
lv =0
location_start = 0
factor = 1
top_buffer=2
side_buffer=2
current_direction ="A"
current_word = ""
current_row=2000
current_col=2000
cursor_row = current_row
cursor_col = current_col
across_clues={}
down_clues = {}
mapper ={}
answersheet=[]
active_cursor=[]

p = puz.read('three.puz')
numbering = p.clue_numbering()
ser = serial.Serial("/dev/tty.usbmodem141101", baudrate="9600",timeout=0.001)
tempframe=bytearray([])
temp =np.empty([len(p.fill)])
Matrix = np.array( [[0 for x in range(p.width)] for y in range(p.height)])
displayframe=np.array( [[0 for x in range(34)] for y in range(34)])
answer_matrix = [[0 for x in range(p.width)] for y in range(p.height)]



"""-----DEBUG FUNCTION----"""
def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)



"""------------------- GRAPHITI INITIALIZATION FUNCTIONS ----------------------------"""
def UpdateScreen (Frame):
    """
    Parameters: Frame- Bytearray of the API command, without the checksum
    Return: prints out [] if success, [ <text> ] if fail
    Function to send data to Graphiti with any particular specified frame. This function automatically adds the checksum
    """
    ### TODO: Rename this to something Better, even in the other Graphoto file

    print "Update Screen Called"
    checksum = 256-sum(Frame[1:])
    for i in range(len(list(Frame))):
        if(i!=0):
            if(list(Frame)[i] == 27 and list(Frame)[i-1] != 27 and list(Frame)[i+1] != 27):
                Frame = Frame[:i]+bytearray([0x1b])+Frame[i:]
        i+=1
    
    Frame = Frame+ bytearray([checksum])
    if (checksum == 27):
        Frame = Frame+ bytearray([checksum])
    #print list(Frame)   
    ser.write(Frame)
    response = ser.readlines()
    response_list = list(response)
    time.sleep(0.02)
    print " ------------------"

    
def RefreshScreen():
    """
    Refreshes the graphiti screen by raising and loweing all pins.
    """
    UpdateScreen(all_up_frame)
    UpdateScreen(all_down_frame)
    
def GetPointHeight(x,y):
    """
    Takes the x,y value 15x15 size, and returns the integer value for the height for that point.
    """
    level = lv
    if(level==0):bg = 0;empty = 2;fill = 1
    if(level ==1):bg = 2;empty =  1;fill =0
    if(level ==2):bg = 2;empty =  0;fill = 1
    element = answersheet[x][y]
    if(element == 'Empty'):return empty
    elif(element =='Closed Box'): return bg
    else: return fill
    
def Img2Screen (level):
    global factor,tempframe, displayframe
    """
    Prints out the crossword with a 4 point boundary around it and a one line buffer between the puzzle and the crossword
    parameters: image file
    """

    print "here"
    if(level==0):bg = 0;empty = 2;fill = 1
    if(level ==1):bg = 2;empty =  1;fill =0
    if(level ==2):bg = 2;empty =  0;fill = 1
    
    limit = 2*(len(Matrix))
    for x in range(1,41):
        print x
        row_frame = image_row_frame + bytearray([chr(x)])
        if(x==2 or x==34):
            for i in range (0,side_buffer-1):row_frame = row_frame + bytearray([0x00,0x00])
            for i in range(0,limit+4):row_frame = row_frame +bytearray([chr(4),0x00])
            while (len(row_frame)<=123):row_frame = row_frame + bytearray([0x00,0x00])
            UpdateScreen(row_frame)
        elif(x==3 or x==33):
            for x in range (0,side_buffer-1):row_frame = row_frame + bytearray([0x00,0x00])
            row_frame = row_frame +bytearray([0x04,0x00])
            for x in range(0,limit+top_buffer):row_frame = row_frame +bytearray([chr(0),0x00])
            row_frame = row_frame +bytearray([0x04,0x00])
            while (len(row_frame)<=123):row_frame = row_frame + bytearray([0x00,0x00])
            UpdateScreen(row_frame)
        
        elif(x>3 and x<33 and x%2 == 0):
            #for filling crosswoed row
            row_frame = row_frame + bytearray([0x04,0x00,0x04,0x00,0x00,0x00])
            #print Matrix[x/2-3]
            for element in answersheet[x/2-2]:
                if (element == 'Empty'):row_frame = row_frame +bytearray([chr(empty),0x00,chr(bg),0x00])
                elif(element == 'Closed Box'):row_frame = row_frame +bytearray([chr(bg),0x00,chr(bg),0x00])
                else:row_frame = row_frame +bytearray([chr(fill),0x00,chr(bg),0x00])
            row_frame = row_frame + bytearray([0x00,0x00,0x04,0x00])
            while (len(row_frame)<=123):row_frame = row_frame + bytearray([0x00,0x00])
            UpdateScreen(row_frame)
            
        elif(x>3 and x<33 and x%2 != 0):
            #for filling empty separation border rows
            if(x == 27):row_frame = row_frame +bytearray([0X1B])
            row_frame = row_frame + bytearray([0x00,0x00,0x04,0x00,0x00,0x00])
            for a in range(len(Matrix)):row_frame = row_frame +bytearray([chr(bg),0x00,chr(bg),0x00])
            row_frame = row_frame + bytearray([0x00,0x00,0x04,0x00])
            while (len(row_frame)<=123):row_frame = row_frame + bytearray([0x00,0x00])
            UpdateScreen(row_frame)


def PrintImg(level):
    RefreshScreen()
    Img2Screen(level)

def InitialSetup(img):
    PrintImg(0)

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

def GenerateAnswerMatrix():
    global answer_matrix,p
    for row in range(0,p.height):
        answer_matrix[row] = list(p.solution[row*p.width:(row*p.width)+p.width])

	    
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
            value=0
            if(int(temp[count]) ==1): value=2
            Matrix[row][element] = value
            mapper[count] = ((2*row+4),(2*element+4))
            count +=1

            
def GenerateClues():
    """
    Initialization Step 3
    Generate across and down clues from the data, and store it in the form of a dictionary {cell:"the clue is ....... of length ...."}
    """

    
    for element in numbering.across:
        across_clues[element['cell']]= "The Across clue is . . . "+str(element['clue'].encode('utf-8').partition("(")[0])+", and is of a total length of "+str(element['len'])
    for element in numbering.down:
        down_clues[element['cell']]= "The Down clue is . . .  "+str(element['clue'].encode('utf-8').partition("(")[0])+", and is of a total length of "+str(element['len'])

def GenerateAnswerSheet():
    global answersheet
    """
    Initialization Step 4
    Generate an answersheet that the user can refer back to as per required
    """

   
    for element in Matrix:
        entry = []
        value=""
        for piece in element:
            if (piece == 2):
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

def AlertPoint(x,y,high,height=None):
    """
    Function: Feedback to the user incase of any form of selection or interaction.
    Parameters: x,y coordinate of the Graphiti pin! NOT THE MATRIX!
                high: 1 to turn on the Alert, and 0 to turn it off.
                height: if being turned off, you must specify a height to reset the pin to after turning off the alert.
    Returns: a height as an integer if alert is toggled on, returns nothing of the alert is toggled off
    """
    print "AlertPoint"
    if (high == 1):
        point_height_frame = point_status_frame + bytearray(chr(x)) + bytearray(chr(y))
        UpdateScreen(point_height_frame)
        height_response = ser.readline()
        while (height_response == None  or len(height_response)==0):
            height_response = ser.readline()
        if (ord(list(height_response)[-1]) ==10):
            resp2= ser.readline()
            height_response=height_response+resp2
##            print "height resp extended 1"
##            print list(height_response)
##            print ord(list(height_response)[-1])
            if (ord(list(height_response)[-1]) ==10):
                resp2= ser.readline()
                height_response=height_response+resp2[0]
##                print "height response extended 2: "
##                print list(height_response)
        height_response2 =  ord(list(height_response)[4])
        if(list(height_response)[2]==chr(x) and list(height_response)[3]==chr(y)):
            point_notify1 = point_update_frame +bytearray([(x),(y),4,0x02])
            UpdateScreen(point_notify1)
            time.sleep(0.01)
        return height_response2
    elif(high == 0):
        time.sleep(0.01)
        point_notify1 = point_update_frame +bytearray([(x),(y),height,0x00])
        UpdateScreen(point_notify1)    


def SpeakClue(direction,x,y):
    global current_direction,current_row,current_col
    """
    Function
    Parameters: Direction (A for across and D for down), x and y coordinates on the crossword.
    Return: Clue in the form of a string

    This function returns a string of clue that can be announced by system for any direction specified
    """
    ### TODO: Smoothen this function so that if the touch is on a spot that is not a start of the sentence, it specifies that!!.
    ### TODO: Smoothen this function, so that if the the point has an across hint, and user asks for down, it mentions that, and asks user to click the down button instead... good idea?


    if (x > 15 or x<1):x = current_row
    if (y > 15 or y<1):x = current_col
    xclue = 2*x+2
    yclue = 2*y+2
    print "INSIDE GETTING CLUE: "
    print (xclue,yclue)
    print GetCellFromCoord(xclue,yclue)

    current_row = x
    current_col = y
    if (direction == "A"):
        print "Across"
        try :
            clue = across_clues[GetCellFromCoord(xclue,yclue)]
            height = AlertPoint(xclue,yclue,1)
            leng = clue[-1]
            current_direction = direction
            print clue
            system("say 'Point"+str(x)+"comma"+str(y)+". " + clue+" .'" )
            AlertPoint(xclue,yclue,0,height)
            current_row= x ;current_col = y
        except:
            # Attempt: If user asks for a clue from a char in the middle, announce the clue does not start there
            height = 0
            try:
                x_now = x
                y_now = y
                print "supyall", str(Matrix[x_now-1][y_now-1]==1)
                while (Matrix[x_now-1][y_now-1] == 1):
                    x_now -= x_now
                for ex in range(x_now,x+1):
                    temp = AlertPoint(2*ex+2,2*y_now+2,1)
                    height = temp
                clue = across_clues[GetCellFromCoord(x_now,y_now)]
                system("say 'Clues begin from"+str(x_now)+"comma"+str(y_now)+". " + clue+" .'")
                for ex in range(x_now,x+1):
                    AlertPoint(2*ex+2,2*y_now+2,0,height)
                
            except Exception ,e:
                PrintException()
                print "ERROR!!! ",e
                system("Say 'Point"+str(x)+"comma"+str(y)+" does not have a word running across.'")
                AlertPoint(2*ex+2,2*y_now+2,0,height)
    elif (direction == "D"):
        try:
            clue = down_clues[GetCellFromCoord(xclue,yclue)]
            height = AlertPoint(xclue,yclue,1)
            print height
            leng = clue[-1]
            current_direction = direction
            system("Say 'For the point"+str(x)+"comma "+str(y)+"........... '")
            system("Say '"+clue+" .'")
            AlertPoint(xclue,yclue,0,height)
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


def GetLocation(response):
    """
    """
    row = ord(list(response)[2])
    column = ord(list(response)[3])
    if (row%2 !=0): row = row-1
    if(row<4):row =4
    if (column%2 !=0): column = column-1
    if(column<4):column =4
    return((row-top_buffer)/2,(column-side_buffer)/2)

def AnnounceContent(row,column):
    """
    Announces the content from answersheet about what is there under the finger
    Parameters: Row and Column in the format of the memory of the matrix, NOT THE DISPLAY COORDINATES!
    """

    ##TODO: Button to repeat a clue?
    ## TODO: Repeat a clue?
    ## TODO: Announce clues differently?
    height=0
    global current_row,current_col
    board_row = row*2+top_buffer
    board_col = column*2+side_buffer
    current_row = row
    current_col = column
    if(row<=15 and column<=15):
        print (row*2+top_buffer,column*2+side_buffer)
        height = AlertPoint(board_row,board_col,1)
        system("Say 'Selected Point"+str(row)+"comma"+str(column)+" .'" )
        system("Say 'Character stored is   "+answersheet[row-1][column-1]+" .'")
        print answersheet[row-1][column-1]
        AlertPoint(board_row,board_col,0,height)
        
    print "___________________________"

    
def GetLastTouch():
    """
    Gets the last point of touch and returns the  entire response from Graphiti
    parameters: None
    returns: Array of ASCII value of hex character response
    """
    UpdateScreen(last_touch_point_frame)
    print "checking"
    print list(last_touch_point_frame)
    response = ser.readline()
    while (response == None or len(response)==0):
        response = (ser.readline())
    print list(response)
    if (ord(list(response)[-1]) ==10):
        resp2= ser.readline()
        resp3 = response+resp2
        if (ord(list(resp2)[0]) ==10):
            respfinal = ser.readline()
            resp3 = resp3+respfinal

        response=resp3
    if(ord(list(response)[2])>34 or ord(list(response)[3])>34):
        print "This is out of bounds"
        system("say 'Out of bounds'")
        while (response == None or len(response)==0):
            response = (ser.readline())
    
    size = len(list(response))
    for i in range(len(list(response))):
        if(i!=0 and i<size):
            if(ord(list(response)[i]) == 27 and ord(list(response)[i+1]) == 27):
                response = response[:i]+response[i+1:]
                size = size-1
        i+=1
    
    return response


def Keystroke(character,bkspace = None):
    global current_word,cursor_row,cursor_col,charcount,edit_mode_char_len
    current_word = current_word + character
    
    print "CHARCOUNT      :",str(charcount)
    if(bkspace == 1):
        charcount -=1
        UpdateCursor(0)
    else:
        charcount +=1
        if(edit_mode_char_len !=1):UpdateCursor(1)
    
    

def EditModeToggle():
    global edit_mode
    if (edit_mode==1):
        edit_mode = 0
        charcount=1
        UpdateCursor(10000)
    else:
        edit_mode=1
        UpdateCursor(10001)
    pass

def ExitEditModeSequence():
    print"ENTERED EXIT MODE SEQUENCE"
    global active_cursor,edit_mode_char_len,current_word,charcount
    EditModeToggle()
    system("say 'Exiting edit mode. Your word entered was     '"+str(current_word)+"'")
    print active_cursor
    print "exiting..."
    print Matrix
    for point in active_cursor:
        value = Matrix[((point[0]-2)/2)-1][((point[1]-2)/2)-1]
        ht = GetPointHeight(((point[0]-2)/2)-1,((point[1]-2)/2)-1)
        point_notify1 = point_update_frame +bytearray([(point[0]),(point[1]),ht,0x00])
        UpdateScreen(point_notify1)
    active_cursor=[]
    charcount=1
    edit_mode_char_len=0
    current_word=""

    
def UpdateCursor(show):
    global cursor_row,cursor_col,active_cursor
    if (show == 10001 or show == 10000):
        cursor_row = 2*current_row+2
        cursor_col = 2*current_col+2
        point_notify1 = point_update_frame +bytearray([(cursor_row),(cursor_col),4,0x02])
        if (show == 10000):active_cursor=active_cursor+[(cursor_row,cursor_col)]
        UpdateScreen(point_notify1)
        if (current_direction =="D"):cursor_row = cursor_row + 2
        if (current_direction =="A"):cursor_col = cursor_col + 2
        time.sleep(0.01)
    
    if (show == 1):
        print "cursor call"
        point_notify1 = point_update_frame +bytearray([(cursor_row),(cursor_col),4,0x02])
        active_cursor=active_cursor+ [(cursor_row,cursor_col)]
        UpdateScreen(point_notify1)
        time.sleep(0.03)
        print "cursors were: "+str(cursor_row)+" , "+str(cursor_col)
        if (current_direction =="D"):cursor_row = cursor_row + 2
        if (current_direction =="A"):cursor_col = cursor_col + 2
        print "cursors now are : "+str(cursor_row)+" , "+str(cursor_col)
    if (show == 0):
        active_cursor = active_cursor[:-1]
        point_notify1 = point_update_frame +bytearray([(cursor_row),(cursor_col),Matrix[(cursor_row-2)/2-2][(cursor_col-2)/2-2],0x00])
        UpdateScreen(point_notify1)
##        if (current_direction =="D"):cursor_row = cursor_row - 2
##        if (current_direction =="A"):cursor_col = cursor_col - 2
        print "Implement what is to be done in case of a backspace here! "
        




GenerateImage()
GenerateClues()
GenerateAnswerSheet()
GenerateAnswerMatrix()
print "starting up ..."
RefreshScreen
img = matplotlib.image.imread('crossword.png')
InitialSetup(img) #puzzle displayed for the first time
UpdateScreen(button_activate_frame)

while ser.is_open:
    try:
        response_button = ser.readline()
        button_value = list(response_button)
        rest = GetLastTouch
        print button_value
        if (len(list(response_button)) > 0 and (button_value[1]) == "2") :
            print (ord(button_value[3]),ord(button_value[4]))
            if (ord(button_value[4])==2 and ord(button_value[3])==2):
                print "space"
                answer= (0,0)
                start = timeit.timeit()
                response = GetLastTouch()
                answer = GetLocation(response)
                if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32):
                    location_start = timeit.timeit()
                    AnnounceContent(answer[0],answer[1])
                    
            #Keys for navigation or scrolling around words.        
            if( ord(button_value[3]) ==128 and ord(button_value[4]) ==2):
                print "right"
                if (edit_mode ==0):
                    response = GetLastTouch()
                    answer = GetLocation(response)
                    if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32):SpeakClue("A",answer[0],answer[1])
                    else:system("Say 'Try again'")
                elif (edit_mode == 1):
                    if(current_direction == "A"):
                        print "scroll front"
                        charcount +=1
                        cursor_col = cursor_col + 2
                    else:
                        print "use up and down arrow keys to move cursor"
                    
            if( ord(button_value[3]) ==32 and ord(button_value[4]) ==2):
                print "left"
                if (edit_mode == 0):TryRight();
                elif (edit_mode == 1):
                    if (current_direction == "A"):
                        print "scroll back"
                        charcount-=1
                        cursor_col = cursor_col - 2
                    else:
                        print "use up and down arrow keys to move cursor"
                        
            if( ord(button_value[3]) ==64 and ord(button_value[4]) ==2):
                print "down"
                if(edit_mode == 0):
                    response = GetLastTouch()
                    answer = GetLocation(response)
                    if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32): SpeakClue("D",answer[0],answer[1])
                    else: system("Say 'Try again'")
                elif (edit_mode == 1):
                    if(current_direction=="D"):
                        print "scroll front"
                        #change char count makes sense?
                        charcount+=1
                        
                        point_notify1 = point_update_frame +bytearray([(cursor_row),(cursor_col),Matrix[(cursor_row-2)/2-2][(cursor_col-2)/2-2],0x00])
                        UpdateScreen(point_notify1)
                        cursor_row = cursor_row + 2
                    else:
                        print "use right left key to move cursor"
                    
            if( ord(button_value[3]) ==16 and ord(button_value[4]) ==2):
                print "up"
                if( edit_mode ==0): TryDown()
                elif (edit_mode == 1):
                    if(current_direction == "D"):
                        print "scroll back"
                        charcount-=1
                        cursor_row = cursor_row - 2
                    else:
                        print "use right left key to move cursor"
                
            if( ord(button_value[3]) ==1 and ord(button_value[4]) ==2):
                print "select"
                global edit_mode
                if (edit_mode == 0):
                    xclue = 2*current_row+2
                    yclue = 2*current_col+2
                    a = 0;d= 0;
                    try:
                        leng_a= across_clues[GetCellFromCoord(xclue,yclue)][-1]
                        a= 1
                    except Exception ,e:
                        print str(e)
                        print " No clue across"
                    try:
                        leng_d = down_clues[GetCellFromCoord(xclue,yclue)][-1]
                        d = 1
                    except Exception ,e:
                        print str(e)
                        print " No clue down"
                            
                    if (current_direction =="A"):
                        direction = "Across"
                        if (a==1 and d==0):
                            system("say ' "+str(current_row)+"comma"+str(current_col)+" . length"+str(leng_a)+" running Across. You are entering edit mode'")
                            edit_mode_char_len = int(leng_a);EditModeToggle();
                        elif(d==1 and a ==0):
                            system("say '  "+str(current_row)+"comma"+str(current_col)+". the durection is Down. Change direction then select to edit this word.'")
                        elif(a==1 and d==1):
                            system("say '  "+str(current_row)+"comma"+str(current_col)+" . Length"+str(leng_a)+" running Across.You are entering edit mode'")
                            edit_mode_char_len=int(leng_a);EditModeToggle();
                        else:
                            system("say ' Point "+str(current_row)+"comma"+str(current_col)+"'")
                            EditModeToggle()
                    else:
                        direction = "Down"
                        if(d==1 and a ==0):
                            system("say '  "+str(current_row)+"comma"+str(current_col)+" . length"+str(leng_d)+" running Down. You are entering edit mode '")
                            edit_mode_char_len=int(leng_d);EditModeToggle()
                        elif (a==1 and d==0):
                            system("say '  "+str(current_row)+"comma"+str(current_col)+". the direction is Across. Change direction then select to edit this word.'")
                        elif(a==1 and d==1):
                            system("say '  "+str(current_row)+"comma"+str(current_col)+" . Length"+str(leng_d)+" running Down. You are entering edit'")
                            edit_mode_char_len=int(leng_d);EditModeToggle()
                        else:
                            system("say ' Point "+str(current_row)+"comma"+str(current_col)+"'")
                            EditModeToggle()
                else:
                    ExitEditModeSequence()
            
                
            if( ord(button_value[3]) ==0 and ord(button_value[4]) ==2):
                print "buttons yo!"
                if(edit_mode==0 and ord(button_value[2]) ==16):
                    if(lv==0):print"level 1";lv = 1;PrintImg(1)
                    elif(lv ==1):print "level 0";lv = 2;PrintImg(2)
                    elif(lv ==2):lv = 0;PrintImg(0);print"level 0"     
                else:
                    print " Hitting Keyboard",str(edit_mode_char_len)
                    try :
                            character= characterdict [(ord(button_value[2]),ord(button_value[3]))]
                            system("say '"+ character+"'")
                            if (character != "backspace"):
                                if(current_direction == "A"):
                                    char_row = ((cursor_row-2)/2)-1;char_col = ((cursor_col-2)/2)-2
                                if(current_direction == "D"):
                                    char_row = ((cursor_row-2)/2)-2;char_col = ((cursor_col-2)/2)-1
                                answersheet[char_row][char_col] = character
                                Keystroke(character)
                                system("say 'REDUCED!'")
                                edit_mode_char_len = edit_mode_char_len - 1
                            elif(character == "backspace"):
                                if(charcount !=0):
                                    if(current_direction == "A"):
                                        cursor_col = cursor_col - 2
                                        char_row = ((cursor_row-2)/2)-1;char_col = ((cursor_col-2)/2)-2
                                    if(current_direction == "D"):
                                        cursor_row = cursor_row - 2
                                        char_row = ((cursor_row-2)/2)-2;char_col = ((cursor_col-2)/2)-1
                                    answersheet[char_row][char_col] = "Empty"
                                    print answersheet
                                    Keystroke("Empty",1)
                                    edit_mode_char_len = edit_mode_char_len + 1
                                    print "reduced once", str(charcount)
                                    
                            if(edit_mode_char_len == 0):
                                print "exiting with" , str(edit_mode_char_len)
                                ExitEditModeSequence()
                            
                    except Exception, e:
                            PrintException()
                            print str(e)
                            print (ord(button_value[2]),ord(button_value[3]))
                            system('say "Error, character not recognized!"')
                        
                        
                    
                
            UpdateScreen(ack_frame)
    except Exception,e:
        PrintException()
        print str(e)
        ser.close()
        system ("say 'processing ..'")
        time.sleep(1)
        ser.open()
