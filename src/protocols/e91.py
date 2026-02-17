import numpy as np
import random

class Recievers:

    def __init__(self, bases:list):
        self.bases = bases

    def rand_bases(self)->list[float]:
        # append list cos now bases will be floats
        base =  []
        base.append(random.choice(self.bases))
        return base
    
    def measurement(self):
        pass

class Charlie:
    
    def __init__(self):
        pass

    def send_states(self):

        pass

class E91:
    
    def __init__(self, alice:Recievers, bob:Recievers, charlie:Charlie):

        self.alice = alice
        self.bob = bob
        self.charlie = charlie


if __name__ == "__main__":

    alice = Recievers([0.0, 22.5, 45.0])
    bob = Recievers([45.0, 90.0, 135.0])
