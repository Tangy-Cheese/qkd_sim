import numpy as np
from protocols.bb84 import Channel, Eve
import networkx as nx
import matplotlib.pyplot as plt
from networkx import draw

class Node:

    def __init__(self, identity:str)->None:
        
        self.identity = identity
        self.key = []
        self.qber = []
        self.skr = []
        

class Edge:

    def __init__(self, node_1: Node, node_2:Node, distance:int, attenuation:float, eve: Eve | None)->None:
        
        self.node_1 = node_1
        self.node_2 = node_2 
        
        self.channel = Channel(eve, distance, attenuation) 
 
class Network:
    """
    Edge: Channel 
    Weight: Channel object containing QBER, key rate, photon loss
    """
    def __init__(self, nodes:list, links:list[Edge])->None:
        
        self.nodes = nodes
        self.links = links 
        self.graph = {}
        self.adj_list()
        self.adj_mat = self.matrixify_list()

    def adj_list(self)->None:
        
        for node in self.nodes:
            
            self.graph[node] = []

        for link in self.links:
            
            a = link.node_1
            b = link.node_2
            
            edge = link.channel
            
            self.graph[a].append((b, edge))
            self.graph[b].append((a, edge))
        
    def matrixify_list(self)->np.ndarray:
        
        adj_mat = np.zeros((len(self.nodes), len(self.nodes)), dtype=Channel)
        
        node_to_idx = {node: i for i, node in enumerate(nodes)}

        for u, v, t in edges:
            i = node_to_idx[u]
            j = node_to_idx[v]
            weight = 

        adj_mat[i, j] = weight
        adj_mat[j, i] = weight 

        return adj_mat

    def __add__(self, other:"Network")->"Network":
        

        #adding networks will inevitably assume that the channels are added likewise
        # Meaning a __add__() will need to be created for channels.
        #might not make too much sense but will come back to it.
        pass
  
    def visualise(self)->None:
        
        G = nx.Graph() 
        
        for node in self.nodes:
            G.add_node(node.identity)
        
        for node_1 in self.graph:
            for node_2, edge in self.graph[node_1]:

            # avoid duplicate edges
                if not G.has_edge(node_1.identity, node_2.identity):

                    distance = edge.distance

                    G.add_edge(node_1.identity, node_2.identity, weight=distance)
        
        #more scaled to distance network layout
        pos = nx.kamada_kawai_layout(G)

        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue")

        labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        plt.show()


class NetAlgorithms:

    def __init__(self,):
        pass

    def dijkstra(self,):
        #since we wanna maximise the skr, we need to minimise the qber, so we m
        pass


if __name__ == "__main__":
    
    #example network     
    #nodes
    Alice = Node("Alice")
    Bob = Node("Bob")
    Charlie = Node("Charlie")
    David = Node("David")
    Emma = Node("Emma")
    Frank = Node("Frank")
    Grace = Node("Grace")
    Heisen = Node("Heisen")
    Ivan = Node("Ivan")
    Judy = Node("Judy")

    nodes = [
        Alice, Bob, Charlie,
        David, Emma, Frank,
        Grace, Heisen, Ivan, Judy
    ]

    # Create edges (distance km)
    edge_AB = Edge(Alice, Bob, 80, 0.2, eve=None)
    edge_BC = Edge(Bob, Charlie, 60, 0.2, eve=None)

    edge_AD = Edge(Alice, David, 120, 0.2, eve=None)
    edge_BE = Edge(Bob, Emma, 100, 0.2, eve=None)
    edge_CF = Edge(Charlie, Frank, 90, 0.2, eve=None)

    edge_DE = Edge(David, Emma, 70, 0.2, eve=None)
    edge_EF = Edge(Emma, Frank, 50, 0.2, eve=None)

    edge_DG = Edge(David, Grace, 150, 0.2, eve=None)
    edge_GH = Edge(Grace, Heisen, 60, 0.2, eve=None)

    edge_HI = Edge(Heisen, Ivan, 75, 0.2, eve=None)
    edge_IJ = Edge(Ivan, Judy, 85, 0.2, eve=None)

    edge_EH = Edge(Emma, Heisen, 95, 0.2, eve=None)

    edges = [
        edge_AB, edge_BC,
        edge_AD, edge_BE, edge_CF,
        edge_DE, edge_EF,
        edge_DG, edge_GH,
        edge_HI, edge_IJ,
        edge_EH
    ]

    network = Network(nodes, edges)
    network.visualise()

