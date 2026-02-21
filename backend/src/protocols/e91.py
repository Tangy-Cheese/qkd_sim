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
    """ 
    I think we can actually keep this empty or not needed at all?
    From what I can tell, Charlie sends the bell state 

    1/sqrt(2) [|01> - |10>] = |psi^- >

    since the measurement outcome under any rotational basis is always 50/50.
    """
    pass

class E91:
    
    def __init__(self, alice:Recievers, bob:Recievers):

        self.alice = alice
        self.bob = bob

if __name__ == "__main__":

    alice = Recievers([0.0, 22.5, 45.0])
    bob = Recievers([45.0, 90.0, 135.0])
