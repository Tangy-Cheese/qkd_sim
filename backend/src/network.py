import numpy as np
from protocols.bb84 import Channel, Eve
import networkx as nx
import matplotlib.pyplot as plt

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
    def __init__(self, nodes:list[Node], links:list[Edge])->None:
        
        self.nodes = nodes
        self.links = links 
        self.graph = {}
        self.adj_list()

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
        
        node_to_idx = {}

        for link in self.links:

            i = node_to_idx[link.node_1]
            j = node_to_idx[link.node_2]

            adj_mat[i,j] = adj_mat[j,i] = link.channel

        return adj_mat

    def __add__(self, other:"Network")->"Network":
        
        """
        Add multiple networks by increasing the list of nodes
        Adding a list of edge relationships to the existing list

        Any of the adj matrices, lists whatever is preserved in this new network objects via the methods
        adj_list(), matrixify_list()
        """

        #for the case of duplicate nodes, we remove duplicates
        node_map = {}
    
        for node in self.nodes + other.nodes:
            node_map[node.identity] = node

        new_nodes = list(node_map.values())
       
        """
        Links is more complicated, since we want to minimise the photon loss, qber etc.
        I think a viable approach would be to calculate using `BB84`sim the better line (since remember its not just distance based but attenuation based too) and choose that.

        For now lets assume that the other network wont have an edge with the same nodes.
        But this needs to be changed.
        """
        new_links = []
        new_links.extend(self.links)
        new_links.extend(other.links)
         
        return Network(new_nodes, new_links)

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
        
    def bfs_search(self, root:str, target:str)->list[str]:
        """
        To find the shortest path between two nodes in terms of no. edges
        """
        queue = [root] #Start off w root search
        visited = set() 
        visited.add(root)
        parent = {} #BFS tree
        
        while queue:
           
            curr = queue.pop(0) #remove the first el of queue and assigns it to curr

            if curr == target: #Stop the search at destination
                break

            for next in self.graph[curr]: #each key of the graph is in the form of a tuple where the first el is the neighbour node.
              
                neighbour = next[0]
                
                if neighbour not in visited:
                   
                    visited.add(neighbour) # Exists so that the loop doesnt go on forever
                    parent[neighbour] = curr
                    queue.append(neighbour) #The queue will as a result order the 1depth nodes to be searched first as all neighbours of curr need to be visited before moving on.

        if target not in visited: #In the case that the target is disconnected from the network.
            return []
        
        #last node
        path = [target]

        while path[-1] != root: # Keep walking backwards to build the path.
            path.append(parent[path[-1]])

        path.reverse()
        
        return path

class NetAlgorithms:

    def __init__(self, network: Network)->None:
        
        self.network = network 
        
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

