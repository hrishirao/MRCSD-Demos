import numpy as np
from PIL import Image
import matplotlib
from matplotlib.pyplot import cm
from os import system
import sys,linecache, pygame, threading, time, serial, puz ,inflect
from pygame.mixer import music as music


"""Graphiti API Data Frames------------------------------------------------------"""
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
characterdict ={(16,0):'A',(48,0):'B',(17,0):'C',(19,0):'D',(18,0):'E',(49,0):'F',(51,0):'G',(50,0):'H',(33,0):'I',(35,0):'J',(80,0):'K',(112,0):'L',(81,0):'M',(83,0):'N',(82,0):'O',(113,0):'P',(115,0):'Q',(114,0):'R',(97,0):'S',(99,0):'T',(84,0):'U',(116,0):'V',(39,0):'W',(85,0):'X',(87,0):'Y',(86,0):'Z',(128,0):'backspace'}

# DEBUG: Test bytearray for raising 6th row to height 4
test_frame = bytearray([0x1B, 0x18, 0x06, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0x04, 0x00, 0xF2])

"""Constants global---------------------------------------------------------"""
edit_mode = 0
edit_mode_char_len = 0
cursor_live = 0
charcount = 1
game_level = 1
lv =0
v_speed = 300 #Speed of voiceover
top_buffer=2
side_buffer=2
current_direction ="A"
current_word = ""
current_row=1000 #Random default current_row
current_col=1000 #Random default current_col
cursor_row = current_row
cursor_col = current_col
across_clues={}
down_clues = {}
mapper ={}
answersheet=[]
active_cursor=[]

""" Initialization global---------------------------------------------------------"""
p = puz.read('/puzzle/test1.puz')
number_engine = inflect.engine()
numbering = p.clue_numbering()
pygame.mixer.init(frequency=22050, size=-16, channels=2) #initialiing music mixer so it
ser = serial.Serial("/dev/tty.usbmodem143101", baudrate="9600",timeout=0.001)
tempframe=bytearray([])
temp =np.empty([len(p.fill)])
Matrix = np.array( [[0 for x in range(p.width)] for y in range(p.height)])
displayframe=np.array( [[0 for x in range(34)] for y in range(34)])
answer_matrix = [[0 for x in range(p.width)] for y in range(p.height)]



"""DEBUG FUNCTION------------------------------------------------------------------"""
"""
   Print Exception prints out the error at the point where it is called. Line number,and what the error is.
"""
def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)



""" GRAPHITI INITIALIZATION FUNCTIONS ----------------------------"""
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
    time.sleep(0.1)
    print " ------------------"


def RefreshScreen():
    """
        Refreshes the graphiti screen by raising and loweing all pins.
    """
    UpdateScreen(all_up_frame)
    UpdateScreen(all_down_frame)

def GetPointHeight(x,y):
    """
        Parameters: X,Y in 15x15 format
        Return: Integer value for the height of the point mentioned.
        Takes the x,y value 15x15 size, and returns the integer value for the height for that point.
    """
    level = lv
    if(level==0):bg = 0;empty = 2;fill = 1
    if(level ==1):bg = 0;empty =  1;fill =1
    if(level ==2):bg = 2;empty =  0;fill = 1
    element = answersheet[x][y]
    if(element == 'Empty'):return empty
    elif(element =='Closed Box'): return bg
    else: return fill

def Img2Screen (level):
    global tempframe, displayframe
    """
        parameters: level combination 0 : Default
        returns: None
        Prints out the crossword with a 4 point boundary around it and a one line buffer between the puzzle and the crossword

    """
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
            for element in answersheet[x/2-side_buffer]:
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

"""CROSSWORD DISPLAY FUCTIONS -----------------------------"""
GenerateImage()
GenerateClues()
GenerateAnswerSheet()
GenerateAnswerMatrix()

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
        if (p.fill[row] == '-'):    temp[row] = (1)
        else:                       temp[row] = (0)
    MapCellsToMatrix()
    matplotlib.image.imsave('/image/crossword.png', Matrix, cmap=cm.gray)


def MapCellsToMatrix():
    """
        Initialization Step 1.1
        This function creates a map between the cells as the data is stored in .puz and matrix grid, as the interaction happens with the graphiti device.
        The dictionary is called mapper, and is in the format = {cell:(x,y)}
    """
    count = 0
    global Matrix,temp,p
    for row in range(p.height):
        for element in range(p.width):
            value=0
            if(int(temp[count]) ==1): value=2
            Matrix[row][element] = value
            mapper[count] = ((2*row+4),(2*element+4))
            count +=1


def GenerateClues():
    """
        Initialization Step 2
        Generate across and down clues from the data, and store it in the form of a dictionary {cell:"the clue is ....... of length ...."}
    """
    for element in numbering.across:    across_clues[element['cell']]= "The Across clue is . . . "+str(element['clue'].encode('utf-8').partition("(")[0])+", length of "+ str(element['len'])
    for element in numbering.down:      down_clues[element['cell']]= "The Down clue is . . .  "+str(element['clue'].encode('utf-8').partition("(")[0])+", and is of a total length of "+str(element['len'])


def GenerateAnswerSheet():
    global answersheet
    """
        Initialization Step 3
        Generate an answersheet that the user can refer back to as per required
    """
    for element in Matrix:
        entry = []; value="";
        for piece in element:
            if (piece == 2):    value = 'Empty'
            if (piece == 0):    value = 'Closed Box'
            entry.append(value)
        answersheet.append(entry)

def GenerateAnswerMatrix():
    """
        Initialization Step 4
        Function populates an answer_matrix dictionary which is a matrix made of all the character answers
    """
    global answer_matrix,p
    for row in range(0,p.height):   answer_matrix[row] = list(p.solution[row*p.width:(row*p.width)+p.width])



"""INTERACTION FUCTIONS -----------------------------"""
def GetCellFromCoord(x,y):
    """
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
        Parameters: x,y coordinate of the Graphiti pin! NOT THE MATRIX!
                high: 1 to turn on the Alert, and 0 to turn it off.
                height: if being turned off, you must specify a height to reset the pin to after turning off the alert.
        Returns: a height as an integer if alert is toggled on, returns nothing of the alert is toggled off
        Function: Feedback to the user incase of any form of selection or interaction.
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
            if (ord(list(height_response)[-1]) ==10):
                resp2= ser.readline()
                height_response=height_response+resp2[0]
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
        Parameters: Direction (A for across and D for down), x and y coordinates on the crossword.
        Return: Clue in the form of a string
        This function returns a string of clue that can be announced by system for any direction specified
    """
    if (x > 15 or x<1):x = current_row
    if (y > 15 or y<1):x = current_col
    xclue = 2*x+2; yclue = 2*y+2;
    print "INSIDE GETTING CLUE:  " , str( (xclue,yclue)), str(GetCellFromCoord(xclue,yclue))
    current_row = x
    current_col = y
    if (direction == "A"):
        try :
            clue = across_clues[GetCellFromCoord(xclue,yclue)]
            height = AlertPoint(xclue,yclue,1)
            leng = clue[-1]
            current_direction = direction
            print clue
            system("say ' "+number_engine.number_to_words(x)+" comma "+number_engine.number_to_words(y)+clue+".' -r"+str(v_speed)  )
            system("say ' "+number_engine.number_to_words(x)+" comma "+number_engine.number_to_words(y) +clue+".")
            AlertPoint(xclue,yclue,0,height)
            current_row= x ;current_col = y
        except:
            # Attempt: If user asks for a clue from a char in the middle, announce the clue does not start there
            height = 0
            try:
                x_now = x
                y_now = y
                #print "Ping", str(Matrix[x_now-1][y_now-1]==1)
                while (Matrix[x_now-1][y_now-1] == 1):
                    x_now -= x_now
                for ex in range(x_now,x+1):
                    temp = AlertPoint(2*ex+2,2*y_now+2,1)
                    height = temp
                clue = across_clues[GetCellFromCoord(x_now,y_now)]
                system("say 'Clues begin from"+str(x_now)+" comma "+str(y_now)+". " + clue+" .' -r"+str(v_speed)  )
                for ex in range(x_now,x+1):
                    AlertPoint(2*ex+2,2*y_now+2,0,height)
            except Exception ,e:
                PrintException()
                print "ERROR!!! ",e
                system("Say 'Point "+number_engine.number_to_words(x)+" comma "+number_engine.number_to_words(y)+" does not have a word running across.' -r"+str(v_speed)  )
                AlertPoint(2*ex+2,2*y_now+2,0,height)
    elif (direction == "D"):
        try:
            clue = down_clues[GetCellFromCoord(xclue,yclue)]
            height = AlertPoint(xclue,yclue,1)
            print height
            leng = clue[-1]
            current_direction = direction
            system("Say 'For the point"+number_engine.number_to_words(x)+" comma "+number_engine.number_to_words(y)+"........... ' -r"+str(v_speed)  )
            system("Say '"+clue+" .' -r"+str(v_speed)  )
            AlertPoint(xclue,yclue,0,height)
        except:
            system("Say 'Point"+number_engine.number_to_words(x)+" comma "+number_engine.number_to_words(y)+" does not have a word running down.' -r"+str(v_speed)  )
    else:
        print "Error specifying the driection!!!!!"


def Edit(x,y):
    """

    """

    if (current_direction == "A"):
        if(GetCellFromCoord(x,y) in across_clues):      print "Write across !"
        else:                                           print "You cannot edit the word running across"
    elif (current_direction == "D"):
        if(GetCellFromCoord(x,y) in down_clues):        print "Write down !"
        else:                                           print "You cannot edit the word running down"


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
    print "Inside Announce Content"
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
        system("Say '"+number_engine.number_to_words(row)+" comma "+number_engine.number_to_words(column)+" .' -r"+str(v_speed)  )
        system("Say '"+answersheet[row-1][column-1]+" .' -r"+str(v_speed)  )
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
        system("say 'Out of bounds' -r"+str(v_speed)  )
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

def sound(argument):
    if(argument =='wrong'):
        music.load("/sound/wrong.wav")
        music.play()
    elif(argument=='correct'):
        music.load("/sound/correct.mp3")
        music.play()
    elif(argument=='blocked'):
        music.load("/sound/blocked.mp3")
        music.play()
    elif(argument=='end'):
        music.load('pop.wav')
        music.play()

    return


def Check(character,x,y):
    print "checking" ,str(answer_matrix[x][y]), answer_matrix[y][x]
    correct =  answer_matrix[x][y]
    if (character == correct):
        print "Correct"
        sound('correct')
        return 1
    else:
        sound('wrong')
        return 0

def Keystroke(character,bkspace = None):
    global current_word,cursor_row,cursor_col,charcount,edit_mode_char_len
    current_word = current_word + character

    print "CHARCOUNT      :",str(charcount)
    if(bkspace == 1):
        UpdateCursor(0)
        UpdateCursor(-1)

    else:
        if(edit_mode_char_len !=1):
            UpdateCursor(0)
            UpdateCursor(1)


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
    system("say 'Exiting edit mode. Your word entered was     '"+str(current_word)+"' -r"+str(v_speed)  )
    print active_cursor
    print "exiting..."
    print Matrix
    for point in active_cursor:
        print point
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


    if (show == 1):
        print "cursor front"
        print "cursors were: "+str(cursor_row)+" , "+str(cursor_col)
        if (current_direction =="D"):cursor_row = cursor_row + 2
        if (current_direction =="A"):cursor_col = cursor_col + 2
        point_notify1 = point_update_frame +bytearray([(cursor_row),(cursor_col),4,0x02])
        UpdateScreen(point_notify1)
        word = answersheet[cursor_row/2-2][cursor_col/2-2]
        if( word!='Empty'):
            system("say '"+answersheet[cursor_row/2-2][cursor_col/2-2] +"' -r"+str(v_speed)  )
        print "cursors now are : "+str(cursor_row)+" , "+str(cursor_col)
        active_cursor=active_cursor+ [(cursor_row,cursor_col)]
    if (show == 0):
        print "cursor close  "
        temp_cursor_row=cursor_row
        temp_cursor_col=cursor_col
        point_notify1 = point_update_frame +bytearray([(cursor_row),(cursor_col),Matrix[(temp_cursor_row)/2-2][(temp_cursor_col)/2-2],0x00])
        UpdateScreen(point_notify1)

    if (show == -1):
        print "cursor previous"
        print "cursors were: "+str(cursor_row)+" , "+str(cursor_col)
        if (current_direction =="D"):cursor_row = cursor_row - 2
        if (current_direction =="A"):cursor_col = cursor_col - 2
        point_notify1 = point_update_frame +bytearray([(cursor_row),(cursor_col),4,0x02])
        active_cursor=active_cursor+ [(cursor_row/2-2,cursor_col/2-2)]
        UpdateScreen(point_notify1)
        word = answersheet[cursor_row/2-2][cursor_col/2-2]
        if( word!='Empty'):
            system("say '"+answersheet[cursor_row/2-2][cursor_col/2-2] +"' -r"+str(v_speed)  )
        print "cursors now are : "+str(cursor_row)+" , "+str(cursor_col)


"""Main program loop---------------------------------------------------------------------"""
"""
    Logic: The program starts by displaying a preset crossword puzzle and
"""
print "starting up ..."
GenerateImage()
GenerateClues()
GenerateAnswerSheet()
GenerateAnswerMatrix()
RefreshScreen()
img = matplotlib.image.imread('/image/crossword.png')
InitialSetup(img) #puzzle displayed for the first time
UpdateScreen(button_activate_frame)

while ser.is_open:
    try:
        response_button = ser.readline()
        button_value = list(response_button)
        rest = GetLastTouch
        if (len(list(response_button)) > 0 and (button_value[1]) == "2") :
            print (ord(button_value[3]),ord(button_value[4]))

            if (ord(button_value[3])==2 and ord(button_value[4])==2):
                print "space"
                answer= (0,0)
                response = GetLastTouch()
                answer = GetLocation(response)
                if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32):
                    AnnounceContent(answer[0],answer[1])

            #Keys for navigation or scrolling around words.
            if( ord(button_value[3]) ==128 and ord(button_value[4]) ==2):
                print "right"
                if (edit_mode ==0):
                    response = GetLastTouch()
                    answer = GetLocation(response)
                    if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32):SpeakClue("A",answer[0],answer[1])
                    else:system("Say 'Try again'-r"+str(v_speed)  )
                elif (edit_mode == 1):
                    if(current_direction == "A"):
                        if(edit_mode_char_len>1):
                            print "scroll front"
                            charcount+=1
                            Keystroke("f")
                            edit_mode_char_len -=1
                            print "EDIT MODE: ",str(edit_mode_char_len)
                        else:
                            print "@@@ Play end of word sound @@@"
                            sound('end')
                    else:
                        music.load("blocked.mp3") ;music.play()
                        print "use up and down arrow keys to move cursor"

            if( ord(button_value[3]) ==32 and ord(button_value[4]) ==2):
                print "left"
                if (edit_mode == 0):TryRight();
                elif (edit_mode == 1):
                    if (current_direction == "A"):
                        if (charcount >1):
                            print "scroll back"
                            charcount-=1
                            Keystroke("Empty",1)
                            edit_mode_char_len +=1
                            print "EDIT MODE: ",str(edit_mode_char_len)
                        else:
                            print "@@@ Play end of word sound @@@"
                            sound('end')
                    else:
                        music.load("blocked.mp3") ;music.play()
                        print "use up and down arrow keys to move cursor"

            if( ord(button_value[3]) ==64 and ord(button_value[4]) ==2):
                print "down"
                if(edit_mode == 0):
                    response = GetLastTouch()
                    answer = GetLocation(response)
                    if(answer[0]>0 and answer[1]>0 and answer[0]<32 and answer[1]<32): SpeakClue("D",answer[0],answer[1])
                    else: system("Say 'Try again'-r"+str(v_speed) )
                elif (edit_mode == 1):
                    if(current_direction=="D"):
                        if(edit_mode_char_len>1):
                            print "scroll front"
                            charcount+=1
                            Keystroke("f")
                            edit_mode_char_len -=1
                        else:
                            print "@@@ Play end of word sound @@@"
                            sound('end')

                    else:
                        music.load("blocked.mp3") ;music.play()
                        print "use right left key to move cursor"


            if( ord(button_value[3]) ==16 and ord(button_value[4]) ==2):
                print "up"
                if( edit_mode ==0): TryDown()
                elif (edit_mode == 1):
                    if(current_direction == "D"):
                        if (charcount >1):
                            print "scroll back"
                            charcount-=1
                            Keystroke("Empty",1)
                            edit_mode_char_len +=1
                        else:
                            print "@@@ Play end of word sound @@@"
                            sound('end')
                    else:
                        music.load("blocked.mp3") ;music.play()
                        print "use right left key to move cursor"


            if( ord(button_value[3]) ==1 and ord(button_value[4]) ==2):
                print "select"
                global edit_mode
                if (current_row <15 and current_col<15 and edit_mode == 0):
                    xclue = 2*current_row+2
                    yclue = 2*current_col+2
                    a = 0;d= 0;
                    try:
                        leng_a= across_clues[GetCellFromCoord(xclue,yclue)].split(" ")[-1]
                        a= 1
                    except Exception ,e:
                        print str(e); print " No clue across"
                    try:
                        leng_d = down_clues[GetCellFromCoord(xclue,yclue)].split(" ")[-1]
                        d = 1
                    except Exception ,e:
                        print str(e); print " No clue down"

                    if (current_direction =="A"):
                        direction = "Across"
                        if(d==1 and a ==0):
                            system("say '  "+number_engine.number_to_words(current_row)+" comma "+number_engine.number_to_words(current_col)+" the durection is Down. Change direction then select to edit this word.' -r "+str(v_speed)  )
                        elif((a==1 and d==1) or (a==1 and d==0) ):
                            system("say '  "+number_engine.number_to_words(current_row)+" comma "+number_engine.number_to_words(current_col)+"  Length"+number_engine.number_to_words(leng_a)+" running Across' -r "+str(v_speed)  )
                            for i in range (0,int(leng_a)):
                                print i
                                print current_row+i
                                print "-------"
                                if(answersheet[current_row-1][current_col-1 + i] != "Empty"):
                                    for j in range (0,int(leng_a)):
                                        system( "say '" +answersheet[current_row-1][current_col-1+j]+ "' -r "+str(v_speed)  )
                                    break
                            system("say 'editing' -r "+str(v_speed)  )
                            word = answersheet[(current_row-1)][(current_col-1)]
                            if( word!='Empty'):system("say ' "+word + "' -r "+str(v_speed)  )

                            edit_mode_char_len=int(leng_a);EditModeToggle();
                        else:
                            system("say '  "+number_engine.number_to_words(current_row)+" comma "+number_engine.number_to_words(current_col)+"' -r "+str(v_speed)  )
                            EditModeToggle()
                    else:
                        direction = "Down"
                        if (a==1 and d==0):
                            system("say '  "+number_engine.number_to_words(current_row)+" comma "+number_engine.number_to_words(current_col)+" the direction is Across Change direction then select to edit this word.' -r "+str(v_speed)  )
                        elif((a==1 and d==1)or (a==0 and d==1)):
                            system("say '  "+number_engine.number_to_words(current_row)+" comma "+number_engine.number_to_words(current_col)+" Length"+number_engine.number_to_words(leng_d)+" running Down' -r "+str(v_speed)  )
                            for i in range (0,int(leng_d)):
                                print i
                                print current_row+i
                                print "-------"
                                if(answersheet[current_row-1 + i][current_col-1] != "Empty"):
                                    for j in range (0,int(leng_d)):
                                        system( "say '" +answersheet[current_row-1 + j][current_col-1]+ "' -r "+str(v_speed)  )
                                    break
                            system ("say 'editing' -r "+str(v_speed)  )
                            word = answersheet[(current_row-1)][(current_col-1)]
                            if( word!='Empty'):system("say ' "+word + "' -r "+str(v_speed)  )

                            edit_mode_char_len=int(leng_d);EditModeToggle()
                        else:
                            system("say '  "+number_engine.number_to_words(current_row)+" comma "+number_engine.number_to_words(current_col)+"' -r "+str(v_speed)  )
                            EditModeToggle()
                elif(current_row <15 and current_col<15 and edit_mode ==1):
                    ExitEditModeSequence()


            if( ord(button_value[3]) ==0 and ord(button_value[4]) ==2):
                print "buttons yo!"
                #print ord(button_value[2])
                if(edit_mode==0 and ord(button_value[2]) ==16):
                    if(lv==0):print"level 1";lv = 1;PrintImg(1)
                    elif(lv ==1):print "level 0";lv = 2;PrintImg(2)
                    elif(lv ==2):lv = 0;PrintImg(0);print"level 0"

                if(edit_mode==0 and ord(button_value[2]) ==8):
                    response = GetLastTouch()
                    answer = GetLocation(response)
                    temp_r = 2*answer[0]+2
                    temp_c = 2*answer[1]+2
                    print answer[0],answer[1]
                    system ("say ' "+ number_engine.number_to_words(answer[0]) + " comma "+ number_engine.number_to_words(answer[1])+"' -r "+str(v_speed)  )
                    system ("say ' "+ answersheet[answer[0]-1][answer[1]-1]+"' -r "+str(v_speed)  )


                elif(edit_mode==1):
                    print " Hitting Keyboard",str(edit_mode_char_len)
                    try :
                        character= characterdict [(ord(button_value[2]),ord(button_value[3]))]
                        system("say '"+ character+"' -r "+str(v_speed)  )
                        if (character != "backspace"):
                            if(current_direction == "A"):char_row = ((cursor_row)/2)-2;char_col = ((cursor_col)/2)-2
                            if(current_direction == "D"):char_row = ((cursor_row)/2)-2;char_col = ((cursor_col)/2)-2
                            if(Check(character,char_row,char_col)):
                                answersheet[char_row][char_col] = character
                                Matrix[char_row][char_col]=1

                        elif(character == "backspace"):
                            if(current_direction == "A"):char_row = ((cursor_row)/2)-2;char_col = ((cursor_col)/2)-2
                            if(current_direction == "D"):char_row = ((cursor_row)/2)-2;char_col = ((cursor_col)/2)-2
                            answersheet[char_row][char_col] = "Empty"
                            Matrix[char_row][char_col]=2
                            print answersheet
                            print Matrix

                        if(edit_mode_char_len == 0):
                            print "exiting with" , str(edit_mode_char_len)
                            ExitEditModeSequence()
                            print Matrix

                    except Exception, e:
                        PrintException()
                        print str(e)
                        print (ord(button_value[2]),ord(button_value[3]))
                        system("say 'Error, character not recognized!' -r "+str(v_speed) )




    except Exception,e:
        PrintException()
        print str(e)
        ser.close()
        system ("say 'processing .. please try again' -r "+str(v_speed)  )
        time.sleep(1)
        ser.open()
