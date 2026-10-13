import numpy as np
import heapq
from protocols.bb84 import Channel, Eve
import networkx as nx
import matplotlib.pyplot as plt


class Node:
    """Each node represents Alice and/or Bob in a networked system

    :param identity: The identity is just characterised as a name of string form
    :param key: Each node has an attribute that is empty initially. But this stores the 
        final key shared between the root and the target that results from the run that 
        the network class enforces.
    :param sent_key: The key this node shares with the next node in the path, where this 
        node was the sender. Empty initially.
    :param received_key: The key this node shares with the previous node in the path, where 
        this node was the receiver. Empty initially.
    """
    def __init__(self, identity:str)->None:
        """Class constructor for each node 

        :param identity: String of name
        """
        self.identity = identity
        self.key = ""
        self.sent_key = ""
        self.received_key = ""


class Edge:
    """In a graph, each edge represents a link between two nodes. Or in the instance of Quantum Key
    Distribution, the presence of a quantum channel.

    :param node_1: A node which can either send or receive
    :param node_2: A second node which can either send or receive
    :param channel: The quantum channel which links the two nodes, characterised by the channel class 
        from protocols/bb84.py
    """
    def __init__(self, node_1: Node, node_2:Node, distance:int, attenuation:float, eve: Eve | None)->None:
        """Edge class constructor

        :param node_1: A node which can either send or receive
        :param node_2: A second node which can either send or receive
        :param distance: Physical distance between the two nodes in Km
        :param attenuation: Optical fibe attenuation constant 
        :param eve: Whethere there exists an Eavesdropper or not in the channel
        """
        self.node_1 = node_1
        self.node_2 = node_2 
        
        self.channel = Channel(eve, distance, attenuation) 


class Network:
    """The network class forms the main underlying object for the connections between all the nodes.

    :param nodes: A list of all of the participating nodes in the network
    :param links: A list of all the links connecting nodes
    :param graph: Store of the Adjacency list that connects all the nodes and edges
    """
    def __init__(self, nodes:list[Node], links:list[Edge])->None:
        """Network constructor 

        :param nodes: List of participating nodes
        :param links: List of all the links between the nodes
        """
        self.nodes = nodes
        self.links = links 
        self.graph = {}
        self.adj_list()

    def adj_list(self)->None:
        """This function fills in the adjacency list attribute of the network class. The adjacency list is created
        from the relation shipe between each node to every other node it is connected to.
        """
        for node in self.nodes:
            
            self.graph[node] = []

        for link in self.links:
            
            a = link.node_1
            b = link.node_2
            
            edge = link.channel
            
            self.graph[a].append((b, edge))
            self.graph[b].append((a, edge))
        
    def matrixify_list(self)->np.ndarray:
        """Method that churns out the adjacency matrix. May be useful for calculations further down the line.

        :return: Numpy array storing the adjacency matrix
        """
        adj_mat = np.zeros((len(self.nodes), len(self.nodes)), dtype=Channel)
        
        node_to_idx = {node: idx for idx, node in enumerate(self.nodes)}

        for link in self.links:

            i = node_to_idx[link.node_1]
            j = node_to_idx[link.node_2]

            adj_mat[i,j] = adj_mat[j,i] = link.channel

        return adj_mat

    def __add__(self, other:"Network")->"Network":
        """Add multiple networks by increasing the list of nodes
        Adding a list of edge relationships to the existing list

        Any of the adj matrices, lists whatever is preserved in this new network objects via the methods
        adj_list(), matrixify_list()

        :param other: Other is another network object. 
        :return: Network class which is the combined two networks
        """
        #for the case of duplicate nodes, we remove duplicates
        node_map = {}
    
        for node in self.nodes + other.nodes:
            node_map[node.identity] = node

        new_nodes = list(node_map.values())
       
        """
        Links are more complicated, since we want to minimise the photon loss, qber etc.
        When both networks have an edge with the same nodes, the better line is chosen. The better 
        line is the one with the lower total loss (since remember its not just distance based 
        but attenuation based too).
        """
        best_links = {}

        for link in self.links + other.links:

            pair = frozenset((link.node_1.identity, link.node_2.identity))

            if pair not in best_links or link.channel.loss() < best_links[pair].channel.loss():
                best_links[pair] = link

        #Links are rebuilt so that they point to the nodes that survived the duplicate removal
        new_links = []

        for link in best_links.values():

            a = node_map[link.node_1.identity]
            b = node_map[link.node_2.identity]

            edge = link.channel

            new_links.append(Edge(a, b, edge.distance, edge.attenuation, edge.eve))
         
        return Network(new_nodes, new_links)

    def visualise(self)->None:
        """Method to visualise networks of the network class using NetworkX package.
        """
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
        
    def bfs_search(self, root:Node, target:Node)->list[Node]:
        """Finding the shortest path between two nodes in terms of edges. Does this via breadth 
        search first where the closest layer of nodes are all searched first. 

        :param root: The starting node of the search
        :param target: The final node of the search
        :return: A list of nodes connecting the starting node to the ending node
        """
        queue = [root] #Start off w root search
        visited = set() 
        visited.add(root)
        parent = {} #BFS tree
        
        while queue:
           
            curr = queue.pop(0) #remove the first el of queue and assigns it to curr

            if curr == target: #Stop the search at destination
                break

            for next in self.graph[curr]: 
                #each key of the graph is in the form of a tuple where the first el is the neighbour node.
              
                neighbour = next[0]
                
                if neighbour not in visited:
                   
                    visited.add(neighbour) # Exists so that the loop doesnt go on forever
                    parent[neighbour] = curr
                    queue.append(neighbour) 
                    #The queue will as a result order the 1 depth nodes to be 
                    #searched first as all neighbours of curr need to be visited before moving on.

        if target not in visited: #In the case that the target is disconnected from the network.
            return []
        
        #last node
        path = [target]

        while path[-1] != root: # Keep walking backwards to build the path.
            path.append(parent[path[-1]])

        path.reverse()
       
        return path 

class NetAlgorithms:
    """Algorithms applied to the network (WIP)

    :param network: The said network
    """
    def __init__(self, network: Network)->None:
        
        self.network = network 
        
    def dijkstra(self, root:Node, target:Node)->list[Node]:
        """Finding the best path between two nodes for key distribution using Dijkstra's algorithm.
        Every link in the path makes its own key, so the secure key rate of the whole path is only 
        as good as its worst link. The best path is therefore the one whose worst link has the 
        lowest loss. Between paths with an equally bad worst link, the lower total loss is preferred.

        :param root: The starting node of the search
        :param target: The final node of the search
        :return: A list of nodes connecting the starting node to the ending node
        """
        #since we wanna maximise the skr, we need to minimise the qber, so we minimise the loss
        best = {root: (0, 0)} #cost of reaching each node as (worst link loss, total loss)
        parent = {}
        visited = set()

        count = 0 #Exists so that the heap never has to compare two nodes on a tie
        heap = [(0, 0, count, root)]

        while heap:

            worst, total, _, curr = heapq.heappop(heap) #cheapest node that has not been visited

            if curr in visited:
                continue

            visited.add(curr)

            if curr == target: #Stop the search at destination
                break

            for neighbour, channel in self.network.graph[curr]:

                if neighbour in visited:
                    continue

                loss = channel.loss()
                cost = (max(worst, loss), total + loss)

                if neighbour not in best or cost < best[neighbour]:

                    best[neighbour] = cost
                    parent[neighbour] = curr

                    count += 1
                    heapq.heappush(heap, (cost[0], cost[1], count, neighbour))

        if target not in visited: #In the case that the target is disconnected from the network.
            return []

        #last node
        path = [target]

        while path[-1] != root: # Keep walking backwards to build the path.
            path.append(parent[path[-1]])

        path.reverse()

        return path


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

