import network as nw
import protocols.bb84
from QKD_utils import XOR


class Simulation:
    """The mains simulation class which runs the whole network along with the QKD protocols.
    (WILL ADD MULTIPROTOCOL LAYERS LATER)
    
    :param network: Network which is simulating (Assumed to be just BB84)
    """
    def __init__(self, network:nw.Network)->None:
        """Simulation class constructor

        :param network: Network that the simulation will be run on
        """
        self.network = network

    def run(self, root:nw.Node, target:nw.Node, key_length:int, dark_count_rate:float)->None:
        """How does the simulation run:

        1) We use bsf search to find a path of nodes connecting the root to the target
        2) For every node in the other than the last, the node is sending a key and the 
        next node is receiving a key.
        3) We check in the adjacency list the keys where for the sending node, if the first element 
        is the recieving node, then the channel between them is the correct quantum channel object to use.
        4) We then set the link between the two nodes to be the channel.
        5) Construct a temporary Alice and Bob relationship for the sending and recieving node.
        6) Create a BB84 protocol object using all the constituents and run it. Storing the result as a 
        dictionary. Note run() in this step is polymorphic applying to the bb84 class.
        7) From the result gather the keys and set them as attrubutes of their relevant node class. Likewise,
        storing qber and skr in the link channels. 
        (WIP WILL IMPLEMENT SENT KEY AND RECIEVED KEY ATTRIBUTES IN NODES SINCE THEY STORE MULTIPLE)
        8) Destruct the temporary classes for memory efficiency.

        Note the purpose of running this is to fill in the missing attributes for the node and linke classes
        in networks. All the data needed to perform calculations and analyses.


        :param root: Starting node
        :param target: Ending node
        :param key_length: How many bits The first node sends
        :param dark_count_rate: The dark count rate of all of the nodes (WIP As each node may
            have a different dark count rate)
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

                #We add key attributes to the nodes
                sending_node.key = result["keys"]["corrected_key"]
                recieving_node.key = result["keys"]["corrected_key"]

                #ADding attributes to channel now
                link.qber = result["measurements"]["error_rate"]
                link.skr = result["measurements"]["secure_key_rate"]
                
                del sender
                del reciever
                del net
    
    def evaluate_path_security(self, root:str, target:str)->dict:
        """Method calculating overall path securities (WIP)

        :param root: Starting node
        :param target: Target node
        :return: Security results in a dictionary
        """
        results = {
            "root" : root,
            "target" : target,

            "network":{
                "distance": ....,
                "number_of_secure_nodes": ...,
            },

            outcomes:




        }


        return results

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

    sim.run(Adam, Kyle, 1000000, 0.01)



    
