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

    def run(self, root:nw.Node, target:nw.Node, key_length:int, dark_count_rate:float)->dict:
        """How does the simulation run:

        1) We use Dijkstra's algorithm to find the lowest loss path of nodes connecting the root to the target
        2) For every node in the other than the last, the node is sending a key and the 
        next node is receiving a key.
        3) We check in the adjacency list the keys where for the sending node, if the first element 
        is the recieving node, then the channel between them is the correct quantum channel object to use.
        4) We then set the link between the two nodes to be the channel.
        5) Construct a temporary Alice and Bob relationship for the sending and recieving node.
        6) Create a BB84 protocol object using all the constituents and run it. Storing the result as a 
        dictionary. Note run() in this step is polymorphic applying to the bb84 class.
        7) From the result gather the secure keys and set them as attrubutes of their relevant node class.
        The sending node stores it as its sent key and the receiving node as its received key. Likewise,
        storing qber and skr in the link channels. 
        8) Destruct the temporary classes for memory efficiency.
        9) Relay the root's key along the path. Every node in between is a trusted node, which encrypts 
        the key using XOR with the key it shares with the next node. The next node decrypts it with the
        same key. At the end the root and the target hold the same final key.

        Note the purpose of running this is to fill in the missing attributes for the node and linke classes
        in networks. All the data needed to perform calculations and analyses.


        :param root: Starting node
        :param target: Ending node
        :param key_length: How many bits The first node sends
        :param dark_count_rate: The dark count rate of all of the nodes (WIP As each node may
            have a different dark count rate)
        :raises ValueError: If the root and target are the same node or no path connects them
        :return: security eval including all the main results in the form of a dict 
        """
        if root == target:
            raise ValueError("Root and target must be different nodes.")

        path = nw.NetAlgorithms(self.network).dijkstra(root, target)

        if not path:
            raise ValueError(f"No path between {root.identity} and {target.identity}.")

        path_distance = 0
        n_secure_nodes = len(path) - 2
        link_results = []

        for i in range(len(path) - 1):
            sending_node = path[i]
            receiving_node = path[i + 1]

            #If two links join the same nodes then the one with the lower loss is used
            channel = None
            for neighbour, ch in self.network.graph[sending_node]:
                if neighbour == receiving_node and (channel is None or ch.loss() < channel.loss()):
                    channel = ch

            if channel is None:
                continue

            path_distance += channel.distance

            sender = protocols.bb84.Alice(key_length)
            receiver = protocols.bb84.Bob(key_length, dark_count_rate)
            bb84_run = protocols.bb84.BB84(sender, receiver, channel)
            result = bb84_run.run()

            sending_node.sent_key = result["keys"]["secure_key"]
            receiving_node.received_key = result["keys"]["secure_key"]

            channel.qber = result["measurements"]["error_rate"]
            channel.skr = result["measurements"]["secure_key_rate"]

            link_results.append({
                "from": sending_node.identity,
                "to": receiving_node.identity,
                "qber": channel.qber,
                "skr": channel.skr,
                "distance_km": channel.distance
            })

            del sender, receiver, bb84_run

        #XOR needs keys of the same length, so the final key is as long as the shortest link key.
        #If any link aborted then its key is empty and so is the final key.
        final_length = min(len(node.sent_key) for node in path[:-1])

        root.key = root.sent_key[:final_length]
        relayed_key = root.key

        for i in range(1, len(path) - 1):
            trusted_node = path[i]
            next_node = path[i + 1]

            #This is the only thing sent publicly, useless without the key of the link
            encrypted_key = XOR(relayed_key, trusted_node.sent_key[:final_length])

            relayed_key = XOR(encrypted_key, next_node.received_key[:final_length])

        target.key = relayed_key

        sim_qber = max((r["qber"] for r in link_results), default=0)
        sim_skr = min((r["skr"] for r in link_results), default=0)

        return {
            "root": root.identity,
            "target": target.identity,
            "network": {
                "distance_km": path_distance,
                "number_of_secure_nodes": n_secure_nodes,
                "links": link_results
            },
            "security": {
                "secure_key_rate": sim_skr,
                "qubit_error_rate": sim_qber,
                "final_key_length": final_length
            }
        }


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
