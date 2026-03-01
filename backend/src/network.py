import numpy as np
from protocols.bb84 import Channel 

class Network:
"""
Edge: distance
Weight: Channel object containing QBER, key rate, photon loss
"""
    def __init__(self, nodes:list, channels:list[Channel]->None:
        """
        Channel needs to be modified in the form Channel(Sender:Alice, Reciever:Bob, *) so we know which nodes the channel is connecting
        """
        
        self.nodes = nodes
        self.edges = channels
        self.graph = {}
        self.adj_list()

    def adj_list(self):
        
        for node in self.nodes:
            
            self.graph[node] = []

        for channel in self.edges:
            
            sender = channel.sender
            reciever = channel.reciever
    
            self.graph[sender].append((reciever, channel)) 
            self.graph[reciever].append((sender, channel))


class NetAlgorithms:

    def __init__(self,):
        pass

    def dijkstra(self,):
        pass


if __name__ == "__main__":

    pass
