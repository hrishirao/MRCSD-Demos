import osmnx as ox
import matplotlib.pyplot as plt
G = ox.graph_from_bbox(37.79324, 37.78892,-122.43115, -122.43658,network_type='drive')
G_projected = ox.project_graph(G)
##ox.plot_graph(G_projected,save = True,filename = "maps", show = False, bgcolor = "#000000",dpi=300, edge_linewidth=6)
#ox.save_gdf_shapefile(G_projected)
#plt.savefig("map.png")
nodes, edges = ox.graph_to_gdfs(G)
##for element in nodes['geometry']:
##    print element
##    print element.x, element.y
##    print " --------------------"

def FilterContains (value):
    counter = 0
    for coordinate in edges['geometry']:
        counter +=1
        if (value == coordinate):
            print edges['name'][counter-1]
            
for coordinates in edges['geometry']:
    FilterContains(coordinates)
