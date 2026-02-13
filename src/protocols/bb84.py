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

        #print(f"Alice's secret key is {key}")
        return key
    
    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "Z"]
        for _ in range(self.length):
            basis += random.choice(bases)

        #print(f"Alice random basis choices are {basis}")
              
        return basis

class Bob:

    def __init__(self, length:int):
        self. length = length

    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "H"]
        for _ in range(self.length):
            basis += random.choice(bases)

        #print(f"Bob random basis choices are {basis}")
              
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

        secret_key = alice.rand_key()
        alice_basis = alice.rand_basis()
    
    def quantum_encoding(self):
        
        quantum_state = ""

        for i in zip(self.secret_key, self.alice_basis):
            if i[0] == "0" and i[1] == "Z":
                quantum_state += "0"

            if i[0] == "0" and i[1] == "X":
                quantum_state += "+"
                
            if i[0] == "1" and i[1] == "Z":
                quantum_state += "1"

            if i[0] == "1" and i[1] == "X":
                quantum_state += "-"
            
            return quantum_state
        
    def key_sift(self):
        pass

    
if __name__ == "main":

    Alice = Alice(5)
    Bob = Bob(5)
    print(Alice.rand_basis, Alice.rand_key)

    protocol = BB84(Alice, Bob)

    print(protocol.quantum_encoding())