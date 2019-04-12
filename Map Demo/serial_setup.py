import serial
import time
from PIL import Image,ImageDraw
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import sys
import math as Math
from matplotlib import pyplot
import numpy as np
from numpy.linalg import norm
from shapely.geometry import LineString, Point
import osmnx as ox
import matplotlib.pyplot as plt
from figures import SIZE, set_limits, plot_coords, plot_bounds, plot_line_issimple
from os import system
from math import sin, cos, atan2, sqrt, degrees, radians, pi
from geopy.distance import great_circle as distance
import geopy.point as gp
import time
##from plot_linestring_example import RunThis

"""
Initialization variables for the device
"""
epsilon = sys.float_info.epsilon
shortest = 500.000000000000000000000000
closest_street=""
closest_street_2 = ""
street_2_counter =0
on_line = False
shortest_line = LineString([(0, 0), (1, 1)])
second_shortest_line = LineString([(0, 0), (1, 1)])
fillmore_point = Point(-122.435076,37.791517)
location_point = Point(-122.434286,37.790951)
clay_point = Point(-122.432635,37.791110)
webster_point = Point( 0,0)
point_gp = gp.Point(latitude =0,longitude=0)
point=Point( -122.433423,37.789927)
##Latitude and longitude of the box of area covered on the map
left = -83.7410
right = -83.73698
top = 42.28126
bottom = 42.27850
angle = 1.5 #-9.5 for sf
threshold = (distance((top,left),(bottom,right)).kilometers-1.05 )/10

print threshold

ser = serial.Serial("/dev/tty.usbmodem143101", baudrate="115200",timeout=0.001)
## Data frames for API commands
all_up_frame = bytearray([0x1B,0x16,0x02])
success_frame = bytearray([0x1B,0x51])
fail_frame = bytearray([0x1B,0x52])
all_down_frame = bytearray([0x1B,0x16,0x03])
image_row_frame = bytearray([0x1B,0x18])
WriteMessage_frame = bytearray([0x1B,0x24])
gesture_frame = bytearray([0x1B,0x41,0x01])
last_touch_point_frame = bytearray([0x1B,0x44])
button_activate_frame = bytearray([0x1B,0x31,0x01])
success_frame = bytearray([0x1B,0x53,0x00,0xAD])
image_size = 35
gesture_enabled = False
message= "hello"
plot_h = 0
plot_w = 0
answer_streets={}

def UpdateScreen (Frame):
    checksum = sum(Frame) #adding software checksum
    Frame.extend((checksum // 256, checksum % 256))
    ser.write(Frame)
    response = ser.readlines()
    response_list = list(response)
    success_list = list(str(success_frame))
    success_check = success_list[0]+success_list[1]+success_list[2]+success_list[3]
##    if (len(response_list) == 0):
##        return
##    if ( response_list[0] == success_check):
##        print 'success'
####    response = ""
##    print response


def Img2Screen (image):
    img =  image.resize((int(image.width* factor), int(image.height * factor)))
    compass = Image.open('compass.png').convert('L')
    compass  = compass.resize((5,5))
    compass_WIDTH ,compass_HEIGHT  = compass.size
    WIDTH, HEIGHT = img.size
    data = list(img.getdata())# convert image data to a list of integers # convert that to 2D list (list of lists of integers)
    data = [data[offset:offset+WIDTH] for offset in range(0, WIDTH*HEIGHT, WIDTH)]
    compass_data = list(compass.getdata())# convert image data to a list of integers # convert that to 2D list (list of lists of integers)
    compass_data = [compass_data[compass_offset:offset+compass_WIDTH] for compass_offset in range(0, compass_WIDTH*compass_HEIGHT, compass_WIDTH)]
    chars = '1234'  # Change as desired for the height of the pins.
    scale = (len(chars)-1)/255.
    row_count = row_buffer
    compass_row_count =0
    
    for i in range(0,len(data)):
##        time.sleep(0.01)
        print i
        row = data[i]
        hex_row = chr(row_count)
        row_frame = image_row_frame +bytearray([hex_row])
        print list(row_frame)
        if(i == 24):
            print "Exception line"
            row_frame = row_frame +bytearray([0X1B])
            print list(row_frame)
##        print "row_frame", str(int(row[1]*scale))
        instance = next((i for i, x in enumerate(row) if x), None)
##        if(row[instance] >0 and row[instance+1]>0 and row[instance+2] >0):
##            row  _frame = row_frame +bytearray([int(row[instance+1]*scale)])+ bytearray([0x00])
##            row_frame = row_frame +bytearray([int(row[instance+1]*scale)])+ bytearray([0x00])
##            row_frame = row_frame +bytearray([int(row[instance+1]*scale)])+ bytearray([0x00])
##        else:
##            row_frame = row_frame + bytearray([0x00,0x00])
##            row_frame = row_frame + bytearray([0x00,0x00])
##            row_frame = row_frame + bytearray([0x00,0x00])
##        print row
        for j in range (0,len(row)):
            value = row[j] 
            row_frame = row_frame + bytearray([int(value*scale)])+bytearray([0x00])
        
            
        if (row_count > 33 and row_count < 39):
            while(len(row_frame)<114):
                row_frame = row_frame + bytearray([0x00,0x00]) 
            while(len(row_frame)==115):
                for i in range(0,4):                    
                    compass_value = compass_data[compass_row_count][i]
                    row_frame = row_frame + bytearray([int(compass_value*scale)])+bytearray([0x00])
            compass_row_count+=1                   
        else:
            while (len(row_frame)<=123):
                row_frame = row_frame + bytearray([0x00,0x00]) 
        print (i == 27)
        if (i == 24):
            row_frame = row_frame + bytearray([0x00,0x00])
            print list(row_frame)
            
        UpdateScreen(row_frame)
        print "---------"
        
        row_count +=1
        
def WriteMessage (message):
    display_message = WriteMessage_frame
    for element in list(message):
        display_message = display_message+bytearray([element,1])
    while (len(display_message)<=42):
               display_message = display_message+bytearray([" ",0])
    display_message = display_message + bytearray([0x00])
    UpdateScreen(display_message)

def RefreshScreen():
    UpdateScreen(all_down_frame); UpdateScreen(success_frame)
    

##def ToggleGestureEnable ():
##    if gesture_enabled:
##        disable_gesture_frame = gesture_frame + bytearray([0x00])
##        UpdateScreen(disable_gesture_frame);UpdateScreen(success_frame)
##    else:
##        gesture_frame = bytearray([0x1B,0x41,0x01])
##        print "enabled"
##        enable_gesture_frame = gesture_frame
##        UpdateScreen(enable_gesture_frame);
##        UpdateScreen(success_frame)
 
def GetLastTouch():
     UpdateScreen( last_touch_point_frame );


def plot_bounds(ax, ob):
    try:
        x, y = zip(*list((p.x, p.y) for p in ob.boundary))
        ax.plot(x, y, 'o', color='#ffffff', zorder=3)
    except:
        pass

def plot_line(ax, ob):
    x, y = ob.xya
    ax.plot(x, y, color='#bbbbbb', alpha=0.7, linewidth=5, solid_capstyle='round', zorder=2)

def FilterContains (line,edge):
    counter = 0
    for coordinate in edge['geometry']:
        counter +=1
        if (line == coordinate):return edge['name'][counter-1]

def isBetween(line, c):
    """
    Checks and returns bool if the line is between point 
    """
    x, y = zip(*list((p.x, p.y) for p in line.boundary))
    a = Point(x[0],y[0]);b = Point(x[1],y[1])
    crossproduct = (c[1] - a.y) * (b.x - a.x) - (c[0] - a.x) * (b.y - a.y)
    # compare versus epsilon for floating point values, or != 0 if using integers
    if abs(crossproduct) > epsilon:return False
    dotproduct = (c[0] - a.x) * (b.x - a.x) + (c[1] - a.y)*(b.y - a.y)
    if dotproduct < 0:return False
    squaredlengthba = (b.x - a.x)*(b.x - a.x) + (b.y - a.y)*(b.y - a.y)
    if dotproduct > squaredlengthba:return False
    return True

##def CheckShortestDist(p3,x,y):
##
##    dist1 = Math.hypot(np.subtract(x[0], p3.x), np.subtract(y[0], p3.y))
##    dist2 = Math.hypot(np.subtract(x[1], p3.x), np.subtract(y[1], p3.y))
##    if dist1>dist2:
##        return dist2
##    else: return dist1
    
def midpoint(a, b):
    a_lat, a_lon = radians(a.latitude), radians(a.longitude)
    b_lat, b_lon = radians(b.latitude), radians(b.longitude)
    delta_lon = b_lon - a_lon
    B_x = cos(b_lat) * cos(delta_lon)
    B_y = cos(b_lat) * sin(delta_lon)
    mid_lat = atan2(
        sin(a_lat) + sin(b_lat),
        sqrt(((cos(a_lat) + B_x)**2 + B_y**2))
    )
    mid_lon = a_lon + atan2(B_y, cos(a_lat) + B_x)
    # Normalise
    mid_lon = (mid_lon + 3*pi) % (2*pi) - pi
    return gp.Point(latitude=degrees(mid_lat), longitude=degrees(mid_lon))

##def distance_to_line(point, p2, p1):
##        x_diff = p2[0] - p1[0]
##        y_diff = p2[1] - p1[1]
##        num = abs(y_diff*point.x - x_diff*point.y+ p2[0]*p1[1] - p2[1]*p1[0])
##        den = Math.sqrt(y_diff**2 + x_diff**2)
##        return num / den

def CoordinateRotate(origin,point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox,oy = origin
    px, py = point

    qx = ox + Math.cos(angle) * (px - ox) - Math.sin(angle) * (py - oy)
    qy = oy + Math.sin(angle) * (px - ox) + Math.cos(angle) * (py - oy)
    return qx, qy

def CheckStreet(point,edges2,axe):
    """
    
    """
    global shortest ,closest_street,closest_street_2,street_2_counter,second_shortest_line,answer_streets
    intersection = False
    intersection_streets =[]
    answer =""
    shortest_distance=0.000
    on_line = False
    shortest = 100
    shortest_line = LineString([(0, 0), (1, 1)])
    second_shortest_line = LineString([(0, 0), (1, 1)])
    print edges2['highway'][1]
    for line in edges2.geometry:
##        print line.boundary
##        print "yolo"
        if (isBetween(line,point_gp)):
            on_line = True
            closest_street_2 = answer
            answer = FilterContains(line,edges2)
            break
        else:
            x,y= zip(*list((p.x, p.y) for p in line.boundary))
            a = gp.Point(longitude = x[0],latitude=y[0])
            b = gp.Point(longitude=x[1],latitude=y[1])
            temp = distance(midpoint(a, b), point_gp)
            if( (distance(a,point_gp) < threshold or distance(b,point_gp)<threshold) and distance(midpoint(a,b),point_gp)>threshold):
                print "here" ,FilterContains(line,edges2)
                
                intersection = True
                if FilterContains(line,edges2) not in intersection_streets:
                    intersection_streets.append(FilterContains(line,edges2))
                
            if (shortest == temp):
                print "equal! and the distance to edge is " ,distance(a,point_gp),distance(b,point_gp)
                pyplot.plot(x,y,color = "green",zorder=5)
                if (closest_street_2 != answer):
                    closest_street_2 = answer
                    second_shortest_line = line

                answer = FilterContains(line,edges2)
                print "=======";print answer
                if answer not in answer_streets:answer_streets[str(answer)] =1
                else: answer_streets[str(answer)] +=1
                
            elif (shortest > temp):
                answer_streets = {}
                shortest = temp
                shortest_line = line
                if (closest_street_2 != answer):
                    closest_street_2 = answer
                answer = FilterContains(line,edges2)
                if answer not in answer_streets:answer_streets[str(answer)] =1
                else: answer_streets[str(answer)] +=1

    print answer_streets
    print intersection_streets
    if intersection == True :
        answer =  ' & '.join(intersection_streets)
        
##    if (len(answer_streets)>0):               
##        highest = max(answer_streets.values())
##        answer =([k for k, v in answer_streets.items() if v == highest])
    
        print "FINAL ANSWER: "
    print shortest
    if (shortest > 0.01):
        print "HOOOOOOHHHHHAAAAAAAAA~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print closest_street_2
        print point.hausdorff_distance(shortest_line)
        print "Second shortest:"
        print point.hausdorff_distance(second_shortest_line)
                                         
    answer = "say '" + answer+"'"
    system(answer)


        
def SayName():
    
    pyplot.close()
    pyplot.clf
    fig2,axe = pyplot.subplots(nrows=1, ncols=2)
    custom_drive = ('["area"!~"yes"]["highway"!~"cycleway|footway|path|pedestrian|steps|track|corridor|'
                        'proposed|construction|bridleway|abandoned|platform|raceway|service"]'
                        '["motor_vehicle"!~"no"]["motorcar"!~"no"]{}'
                        '["service"!~"parking|parking_aisle|driveway|private|emergency_access"]').format(ox.settings.default_access)
    G_new = ox.graph_from_bbox(top, bottom,right, left, network_type= "drive")
    G_projected_new = ox.project_graph(G_new)
    ox.plot_graph(G_projected_new,save = True,filename = "maps_new", show = False,
                  node_color='#FFFFFF',node_edgecolor='#FFFFFF',edge_color='#777777',bgcolor = "#000000",
                  node_zorder=3,dpi=200, edge_linewidth=8,use_geom=True)
    ox.simplify.clean_intersections(G_new,tolerance=100)
    nodes, edges2 = ox.graph_to_gdfs(G_new)
##    for element in edges2:
##        print element
    fig2,axe = pyplot.subplots(nrows=1, ncols=2)
    #axe.axis ('OFF')
    print type(axe)
    #print edges.geom
    for line in edges2.geometry:
        plot_bounds(ax, line)
        plot_line_issimple(ax, line, alpha=1,linewidth=1)
    pyplot.savefig("plot_map",bbox_inches='tight',facecolor='black',pad_inches=0,transperent = True)
    speech =""
    print "checking for this"
    print point.x
    print point.y
    print edges2['name'][1]
    CheckStreet(point,edges2,axe )
    x,y=second_shortest_line.xy
    pyplot.plot(x,y,color = "red",zorder=3)
    pyplot.plot(point.x,point.y,color = "red", marker='o',zorder = 3)
    pyplot.savefig("plot_map",bbox_inches='tight',facecolor='black')
    #pyplot.show()

def PrintImg(imgs):

    global factor, img,image_map_horizontal,image_map_vertical ,nodes,edges, fig,ax,G_projected,threshold
    img = imgs
    w,h = img.size

    if (w>h):
        img = img.crop((0,0,h,h))
        width_compensation = w-h
    else :
        img =img.crop((0,0,w,w))
        height_compensation = h-w

    img.save("mapIsee.png", "png")      
    RefreshScreen()
    print "printed! "
    Img2Screen(img)
    print "------------"




def InitialSetup():

    custom_walk = ('["area"!~"yes"]["highway"="footway"]["foot"!~"no"]["service"!~"private"]{}').format(ox.settings.default_access)
    global factor, img,image_map_horizontal,image_map_vertical ,nodes,edges, fig,ax,G_projected,threshold,G
    G = ox.graph_from_bbox(top, bottom,right, left,custom_filter= custom_walk)#network_type="walk")#
    
##    G_projected = ox.core.graph_from_file("centralcampus.xml", network_type = 'walk',simplify=True,retain_all=False)
##Uncomment this for the original stuff
    G_projected = ox.project_graph(G)
    ox.plot_graph(G_projected,save = True,filename = "maps", show = False,
                  node_color='#999999',node_edgecolor='#999999',edge_color='#999999',bgcolor = "#000000",
                  node_zorder=3,dpi=200, edge_linewidth=8,use_geom=True)
    ox.simplify.clean_intersections(G,tolerance=100)
    
    nodes, edges = ox.graph_to_gdfs(G)
    fig,ax = pyplot.subplots()
    ax.axis ('OFF')
    img = Image.open('images/maps.png').convert('L').rotate(angle)
    img.save('lowered.png')

    height_compensation = 0
    width_compensation = 0
    w,h = img.size
    image_size_w,image_size_h=img.size
    image_map_horizontal = float(left-right)/image_size_w
    image_map_vertical = float(top-bottom)/image_size_h
    if img.width >= image_size and img.height >= image_size:
        if img.height < img.width:
            print "factor denom height is ",str(img.height)
            factor = float(image_size) / img.height
        else:
            print "factor denom width is ",str(img.width)
            factor = float(image_size) / img.width

    PrintImg(img)

print "starting up ..."
##G = ox.graph_from_bbox(top, bottom,right, left, network_type='walk')
##G_projected = ox.project_graph(G)
##ox.plot_graph(G_projected,save = True,filename = "maps", show = False,node_size=80,
##                  node_color='#FFFFFF',node_edgecolor='#FFFFFF',edge_color='#bbbbbb',bgcolor = "#000000",
##                  node_zorder=3,dpi=200, edge_linewidth=9)
##        
##nodes, edges = ox.graph_to_gdfs(G)
##fig,ax = pyplot.subplots(nrows=1, ncols=1)
##ax.axis ('OFF')
##img = Image.open('images/maps.png').convert('L').rotate(-9.5)
##print "printing screen ..."
####img.save('lowered.png')
##height_compensation = 0
##width_compensation = 0
##w,h = img.size
row_buffer = 3
factor = 0.000
image_map_horizontal = 0.00
image_map_vertical = 0.00
test_row_frame =image_row_frame+bytearray([27])
RefreshScreen()
#print list(test_row_frame)
##while(len(test_row_frame)<=123):
##    test_row_frame = test_row_frame + bytearray([0x04,0x00])

##print "------"
#print list(test_row_frame)
#test_row_frame = bytearray([0x1B, 0x18, 0x1B,0x1B, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
#print len(test_row_frame)
#UpdateScreen(test_row_frame)

##print "hereeeeeeee"
InitialSetup()
UpdateScreen(button_activate_frame)
spoken = False
while ser.is_open:

    response_button = (ser.readline())
    button_value = list(response_button)
    print button_value
    if (len(response_button) > 0 and (button_value[1]) == "2") :
        print "here",int(button_value[2].encode("hex"),10),int(button_value[3].encode("hex"),10)
        val = str(int(button_value[2].encode("hex"),10)) + str(int(button_value[3].encode("hex"),10))
        print "also here," ,val
        print button_value[1]
        if (int(val) == 2):
            print "SPEAKING!"
            UpdateScreen(last_touch_point_frame)
            response = ser.readline()
            #UpdateScreen(last_touch_point_frame)
            #response = ser.readline()
            while (response == None or len(list(response)) != 6):
                response = (ser.readline())
##                print list(response)
##                print "a"
            #response = (ser.readline())
            print len(list(response))
            print "~~~~~~~~"
##            response = UpdateScreen( last_touch_point_frame );
            value = list(response)
            print "============"
            print list(response)
            print "-----------"
            if (response != "[]"):
                if len(list(response)) == 6:
                    print "inside"
                    image = Image.open("mapIsee.png")
##                    row = int(value[2].encode("hex"),10) #in dots/
##                    col = int(value[3].encode("hex"),10)-row_buffer
##                    print col
##                    print row
                    print "yyyyy"
                    row = 40-ord(value[2])
                    col = 60-ord(value[3])
                    print col
                    print row
                    img_col_1 = float(row /factor) #to convert it to pixel, we divide by factor = dots/pixel
                    img_row_1 = float(col /factor)
                    print "well"

                    if (row> 35 and col>55):
                        system("say 'map has been rotated by "+str(angle)+" degrees clockwise'")
                    else:
                        system("say 'this street is   '")
                        img_row,img_col = CoordinateRotate(((image.size[0])/2,(image.size[1])/2),(img_row_1,img_col_1),Math.radians(angle))
                        point = Point(float(top + float(img_row*image_map_horizontal)),float(left + float(img_col*image_map_vertical)))
                        print img_row
                        print img_col
                        x=img_row_1
                        y=img_col_1
                        r = 5
                        draw = ImageDraw.Draw(image)
                        draw.ellipse((x-r, y-r, x+r, y+r),fill="blue")
                        image.save('pointedto.png')
                        point_gp = gp.Point(longitude = float(left - float(img_row_1*image_map_horizontal)),latitude = float(top - float(img_col_1*image_map_vertical)))
                        shortest = 10
                        pointed = Point(point_gp[1],point_gp[0])
                        shortest = 10000
                        point_new = Point(point.y,point.x)
                        print point_gp[0],point_gp[1]
                        SayName()
                        spoken = True
                        for element in nodes.osmid:
                            temp = nodes.geometry[int(element)]
                            dist = distance((temp.x,temp.y),(pointed.x,pointed.y)).miles
                            if (shortest >dist):
                                    answer = Point(G.nodes[int(element)]['x'],G.nodes[int(element)]['y'])
                                    shortest = dist
                                    mapoint = element
                        
                        print answer
                        route = nx.shortest_path(G_projected, int(mapoint), 5577776270)
                        ox.plot_graph_route(G_projected, route, save = True,filename = "map_route", show = False,
                                            node_color='#999999',node_edgecolor='#999999',edge_color='#777777',bgcolor = "#000000",
                                            node_zorder=3,dpi=200, edge_linewidth=8,use_geom=True,route_color='#FFFFFF',route_linewidth=10,route_alpha=1)

                        routeimag = Image.open('images/map_route.png').convert('L').rotate(angle)
                        routeimag.save('lowered_route.png')
                        PrintImg(routeimag)
                        

                                                 
##                        An  attempt at finding the closest node to the pointed point:
##                        
##                        
##                        print " Testing: nearest node:"
##                        test_node = ox.utils.get_nearest_node(G_projected, point_gp, method='euclidean', return_dist=False)
##                        print test_node
##                        for element in nodes["osmid"]:
####                            if (element == test_node):
####                                    print "here bro"
##                        route = nx.shortest_path(G_projected, np.random.choice(G_projected.nodes), 
##                        5577776270)
##                        ox.plot_graph_route(G_projected, route, fig_height=10, fig_width=10)
####                        
##                        temp = bytearray([0x1B,0x17,1,1,0x04,0x00])
##                        checksum = sum(temp) #adding software checksum
##                        temp.extend((checksum // 256, checksum % 256))
##                        UpdateScreen(temp)
                        
                        
        elif(val == "020"):
            system("say 'Moving left'")
            print "moving left"
            left = left -0.0015
            right = right - 0.0025
            InitialSetup()
        elif(val =="0900"):
            system("Finding route")
            
        elif(val == "080"):
            system("say 'Moving right'")
            print "moving right"
            left = left +0.0015
            right = right + 0.0025
            
            InitialSetup()
        elif(val == "010"):
            system("say 'Moving up'")
            print "moving up"
            top = top -0.001
            bottom = bottom - 0.001
            InitialSetup()
        elif(val == "040"):
            system("say 'Moving down'")
            print "moving down"
            top = top +0.001
            bottom = bottom + 0.001
            InitialSetup()
        elif(val == "10"):
            print "zoom in"
            left_temp = left +0.0015
            right_temp = right - 0.0025
            top_temp = top -0.001
            bottom_temp = bottom + 0.001
            if(distance((top_temp,left_temp),(bottom_temp,right_temp)).kilometers > 0.05):
                system("say 'Zooming in'")
                left= left_temp
                top = top_temp
                right = right_temp
                bottom = bottom_temp
                InitialSetup()
            else:
                system("say 'Cannot zoom in further!'")
            
        elif(val == "032"):
            print "zoom out"
            left_temp = left -0.0015
            right_temp = right + 0.0025
            top_temp = top +0.001
            bottom_temp = bottom - 0.001
            if(distance((top_temp,left_temp),(bottom_temp,right_temp)).kilometers < 2):
                system("say 'Zooming out'")
                left= left_temp
                top = top_temp
                right = right_temp
                bottom = bottom_temp
                InitialSetup()
            else:
                system("say 'Cannot zoom out further!'")
        
        
        
            #RunThis(point,top,bottom,left,right,edges,ax)

            
            
            
        
ser.close
