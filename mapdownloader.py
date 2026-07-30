import osmnx as ox

location = input("Please specify a location for data download: ")

try:
    G = ox.graph_from_place(location,network_type='drive')
    findingLocation = False
except:
    raise Exception("Location specified does not exist!")

filepath = "./data/"+location+".graphml"
# Download the data to specified filepath
ox.save_graphml(G, filepath)

# Plot graph for viewing after data download
ox.plot_graph(G)


