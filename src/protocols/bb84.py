import numpy as np
import random

def X():
    return 
class Alice:

    def __init__(self, length:int):
        self.length = length

    def rand_key(self)->str:

        key = ""
        for _ in range(self.length):
            key += str(random.randint(0, 1))

        print(f"Alice's secret key is {key}")
        return key
    
    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "H"]
        for _ in range(self.length):
            basis += random.choice(bases)

        print(f"Alice random basis choices are {basis}")
              
        return basis

class Bob:

    def __init__(self, length:int):
        self. length = length

    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "H"]
        for _ in range(self.length):
            basis += random.choice(bases)

        print(f"Bob random basis choices are {basis}")
              
        return basis

class Eve:

    def __init__(self):
        pass

class BB84:

    def __init__(self, alice: Alice, bob: Bob):
        self.alice = alice
        self.bob = bob
        
        if bob.length != alice.length:
            raise Exception("Bob's basis needs to be the same length as Alice's key.")

    def key_sift(self):
        pass


Alice = Alice(5)
Bob = Bob(4)

protocol = BB84(Alice, Bob)

Bob.rand_basis()
Alice.rand_basis()