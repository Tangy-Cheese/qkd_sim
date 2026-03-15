import network as nw
import protocols.bb84
from QKD_utils import XOR


class Simulation:

    def __init__(self, network:nw.Network)->None:

        self.network = network

    def run(self, root:nw.Node, target:nw.Node, key_length:int, dark_count_rate:float)->None:
        """
        dark_count rate needs to be modified as each node dark count rate can be different. !!!!!
        """
        path = self.network.bfs_search(root, target) #list of nodes
       
        for i in range(len(path)-1):
            
            sending_node = path[i]
            recieving_node = path[i+1]
            #consecutive node labelling

            if self.network.graph[sending_node][0] == recieving_node:
                #this checks the corresponoding channel for the first two nodes in the list

                link = self.network.graph[path[i]][1] 
                #if it is then take the next element of that key which is the channel for those two

                sender = protocols.bb84.Alice(key_length) #model the first node as alice
                reciever = protocols.bb84.Bob(key_length, dark_count_rate) #model the second as bob

                net = protocols.bb84.BB84(sender, reciever, link)
                #simulate the two nodes with bb84 and retrive the results
                result = net.run() #dict form 

                """
                NOTE: nodes have attributs SKR, QBER
                might refactor to have these as hidden attributes in Channel class instead.

                More importantly, the Nodes have attributes key, which is very important.
                """
                
                #We add key attributes to the nodes
                sending_node.key = result["keys"]["sifted_alice"]
                recieving_node.key = result["keys"]["sifted_bob"]

                #ADding attributes to channel now
                link.qber = result["measurements"]["error_rate"]
                link.skr = result["measurements"]["secure_key_rate"]
                
                del sender
                del reciever
    
    def evaluate_path_security(self)->None:
        
        pass


if __name__ == "__main__":
    
    #les test this on a super linear simply network

    Adam = nw.Node("Adam")
    Pan = nw.Node("Pan")
    Kyle = nw.Node("Kyle")

    nodes = [Adam, Pan, Kyle]

    edge_AP = nw.Edge(Adam, Pan, distance=20, attenuation=0.2, eve=None)
    edge_PK = nw.Edge(Pan, Kyle, distance=10, attenuation=0.2, eve=None)
    
    edges = [edge_AP, edge_PK]

    network = nw.Network(nodes, edges)
    network.visualise()

    sim = Simulation(network)

    #sim.run()



    
