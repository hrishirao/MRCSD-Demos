import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import osmnx as ox
##left= -122.43618
##right= -122.4294
##top= 37.7934
##bottom = 37.78832
##
##
##
##G = ox.graph_from_bbox(top, bottom,right, left, network_type='drive')
##G_projected = ox.project_graph(G)
##nodes, edges = ox.graph_to_gdfs(G)
##

df = gpd.read_file('export.geojson')
df.plot(column='geometry')
plt.show()
