import network as nw
import protocols.bb84
from QKD_utils import XOR


class Simulation:

    def __init__(self, network:nw.Network)->None:

        self.network = network

    def run(self, root:str, target:str, key_length:int, dark_count_rate:float)->str|None:
        """
        dark_count rate needs to be modified as each node dark count rate can be different. !!!!!
        """
        path = self.network.bfs_search(root, target)
        
        for i in range(len(path)-1):
            
            if self.network.graph[path[i]][0] == path[i+1]:

                link = self.network.graph[path[i]][1]

                sending_node = protocols.bb84.Alice(key_length)
                recieving_node = protocols.bb84.Bob(key_length, dark_count_rate)


                net = protocols.bb84.BB84(sending_node, recieving_node, link)
                result = net.run() 
                
                del sending_node
                del recieving_node
                
                pass   
        #return shared_key

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



    
