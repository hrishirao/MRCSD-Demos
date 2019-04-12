import sys
import math as Math
from os import system
from matplotlib import pyplot
import numpy as np
from numpy.linalg import norm
from shapely.geometry import LineString, Point
import osmnx as ox
import matplotlib.pyplot as plt
from figures import SIZE, set_limits, plot_coords, plot_bounds, plot_line_issimple
epsilon = sys.float_info.epsilon
shortest = 500.000000000000000000000000
closest_street=""
closest_street_2 = ""
street_2_counter =0
on_line = False
shortest_line = LineString([(0, 0), (1, 1)])
second_shortest_line = LineString([(0, 0), (1, 1)])
fillmore_point = Point(  -122.435076,37.791517)
location_point = Point(-122.434286,37.790951)
clay_point = Point(-122.432635,37.791110)
webster_point = Point( -122.432683,37.791411)
point=Point(  -122.435219153, 37.790352)
left= -122.43618
right= -122.4294
top= 37.7934
bottom = 37.78832



def plot_bounds(ax, ob):
    x, y = zip(*list((p.x, p.y) for p in ob.boundary))
    ax.plot(x, y, 'o',linewidth = 6, color='#ffffff', zorder=3)

def plot_line(ax, ob):
    x, y = ob.xya
    ax.plot(x, y, color='#bbbbbb', alpha=1, linewidth=9, solid_capstyle='round', zorder=2)

def FilterContains (line):
    counter = 0
    for coordinate in edges['geometry']:
        counter +=1
        if (line == coordinate):return edges['name'][counter-1]

def isBetween(line, c):
    x, y = zip(*list((p.x, p.y) for p in line.boundary))
    a = Point(x[0],y[0]);b = Point(x[1],y[1])
    crossproduct = (c.y - a.y) * (b.x - a.x) - (c.x - a.x) * (b.y - a.y)
    # compare versus epsilon for floating point values, or != 0 if using integers
    if abs(crossproduct) > epsilon:return False
    dotproduct = (c.x - a.x) * (b.x - a.x) + (c.y - a.y)*(b.y - a.y)
    if dotproduct < 0:return False
    squaredlengthba = (b.x - a.x)*(b.x - a.x) + (b.y - a.y)*(b.y - a.y)
    if dotproduct > squaredlengthba:return False
    return True

def CheckShortestDist(p3,x,y):
    dist1 = Math.hypot(x[0] - p3.x, y[0] - p3.y)
    dist2 = Math.hypot(x[1] - p3.x, y[1] - p3.y)
    if dist1>dist2:
        return dist2
    else: return dist1 


def distance_to_line(point, p2, p1):
        x_diff = p2[0] - p1[0]
        y_diff = p2[1] - p1[1]
        num = abs(y_diff*point.x - x_diff*point.y+ p2[0]*p1[1] - p2[1]*p1[0])
        den = Math.sqrt(y_diff**2 + x_diff**2)
        return num / den

def CheckStreet(point,edges,ax):
    global shortest ,closest_street,closest_street_2,street_2_counter,second_shortest_line
    answer =""
    on_line = False
    for line in edges.geometry:
        if (isBetween(line,point)):
            on_line = True
            answer = FilterContains(line)          
        else:
            x,y= zip(*list((p.x, p.y) for p in line.boundary))
            temp = CheckShortestDist(point,x,y)
            
            if (shortest == temp):
                print "equal!!"
                print x,y,point
                print FilterContains(line), str(temp) 
                second_shortest_line = line
                shortest_line = line
                if (FilterContains(line) != closest_street_2):                   
                    closest_street_2 = FilterContains(line)
                street_2_counter +=1
            elif (shortest > temp):
                shortest = temp
                shortest_line = line
                second_shortest_line = line
                print FilterContains(line), str(temp)
                print "-------------"
                answer =  FilterContains(line)
                
    if (street_2_counter >2):
        answer = closest_street_2
        shortest_line = second_shortest_line
        
    print""
    print "FINAL ANSWER: "
    return answer
fig, ax = pyplot.subplots(nrows=1, ncols=1)
ax.axis ('OFF')

def RunThis(point,top,bottom,left,right,edges,ax):
    
    for line in edges.geometry:
        plot_bounds(ax, line)
        plot_line_issimple(ax, line, alpha=1,linewidth=12)
    pyplot.savefig("plot_map",bbox_inches='tight',facecolor='black',pad_inches=0,transperent = True)    
    response =  CheckStreet(point,edges,ax)
    answer = ('say '+response)
    system(answer)
    print response
    x,y=second_shortest_line.xy
    pyplot.plot(x,y,color = "red",zorder=3)
    pyplot.plot(point.x,point.y,color = "red", marker='o',zorder = 3)
    pyplot.savefig("plot_map",bbox_inches='tight',facecolor='black')


G = ox.graph_from_bbox(top, bottom,right, left, network_type='drive')
G_projected = ox.project_graph(G)
nodes, edges = ox.graph_to_gdfs(G)
RunThis(point,top,bottom,left,right,edges,ax)
pyplot.show()
