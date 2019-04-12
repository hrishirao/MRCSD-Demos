import serial
from os import system
import time
import timeit
import numpy as np
import matplotlib.pyplot as plt

"""Graphiti API Data Frames"""
all_up_frame = bytearray([0x1B,0x16,0x02])
success_frame = bytearray([0x1B,0x51])
fail_frame = bytearray([0x1B,0x52])
all_down_frame = bytearray([0x1B,0x16,0x03])
last_touch_point_frame = bytearray([0x1B,0x44])
button_activate_frame = bytearray([0x1B,0x31,0x01])

ser = serial.Serial("/dev/tty.usbmodem141101", baudrate="115200",timeout=0.0001)





def UpdateScreen (Frame):
    """
    Parameters: Frame- Bytearray of the API command, without the checksum
    Return: prints out [] if success, [ <text> ] if fail
    Function to send data to Graphiti with any particular specified frame. This function automatically adds the checksum
    """

    print "Update Screen"
    print len(Frame)
    checksum = 256-sum(Frame[1:])
    print "Checksum",str(checksum)
    for i in range(len(list(Frame))):
        if(i!=0):
            if(list(Frame)[i] == 27 and list(Frame)[i-1] != 27 and list(Frame)[i+1] != 27):
                Frame = Frame[:i]+bytearray([0x1b])+Frame[i:]
        i+=1
    
    Frame = Frame+ bytearray([checksum])
    if (checksum == 27):
        Frame = Frame+ bytearray([checksum])
    print list(Frame)   
    ser.write(Frame)
    response = ser.readlines()
    response_list = list(response)
    print " ------------------"


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
    print "this is last one", str(ord(list(response)[-1]))
    if (ord(list(response)[-1]) ==10):
        resp2= ser.readline()
        resp3 = response+resp2
        if (ord(list(resp2)[0]) ==10):
            respfinal = ser.readline()
            resp3 = resp3+respfinal
            print list(respfinal)
        print list(resp2)
        print list(resp3)
        response=resp3
    if(ord(list(response)[2])>34 or ord(list(response)[3])>34):
        print list(response)
        print "This is out of bounds"
        while (response == None or len(response)==0):
            response = (ser.readline())
    print (ord(list(response)[2])>34 or ord(list(response)[3])>34)
    print "response",list(response), str(len(response))
    size = len(list(response))
    for i in range(len(list(response))):
        if(i!=0 and i<size):
            if(ord(list(response)[i]) == 27 and ord(list(response)[i+1]) == 27):
                response = response[:i]+response[i+1:]
                size = size-1
        i+=1
    print "sending response",list(response), str(len(response))
    return response


def GetLocation(response):
    """
    """
    row = ord(list(response)[2])
    column = ord(list(response)[3])
    if (row%2 !=0): row = row-1
    if(row<4):row =4
    if (column%2 !=0): column = column-1
    if(column<4):column =4
    return(row,column)


counter = 0
UpdateScreen(button_activate_frame)
plt.axis([0, 40, 0, 60])
while ser.is_open:
    try:
        response_button = ser.readline()
        button_value = list(response_button)
        if (len(list(response_button)) > 0 and (button_value[1]) == "2") :
            print"three"
            if (ord(button_value[4])==2 and ord(button_value[3])==2):
                print "space bar"
                response = GetLastTouch( )
                print"four"
                answer = GetLocation(response)
                x = answer[0]
                y = answer[1]
                plt.scatter(x, y)
                plt.pause(0.05)
                print answer
       
    except Exception,e:
        print "Problem :   " ,str(e)
        ser.close()
        time.sleep(0.3)
        print" Serial crashed"
        ser.open()
        time.sleep(0.1)
plt.show()
