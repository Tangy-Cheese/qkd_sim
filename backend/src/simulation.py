import network as nw
import protocols.bb84

class Simulation:

    def __init__(self, network:nw.Network)->None:

        self.network = network

    def run(self, root:str, target:str)->str|None:
        
        path = self.network.bfs_search(root, target)

        counter = 0

        for i in range(path):
            
            if self.network.graph[path[i]][0] == path[i+1]:

                link = self.network.graph[path[i]][1] 
                net = protocols.bb84.BB84(path[i], path[i+1], link)

                net.run() 

            
        return shared_key
