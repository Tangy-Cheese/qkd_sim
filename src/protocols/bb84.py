import numpy as np
import random

def X():
    return 
class Alice:
    """
    Alice wants to send a secretkey to Bob
    """
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
        bases = ["X", "Z"]
        for _ in range(self.length):
            basis += random.choice(bases)

        #print(f"Bob random basis choices are {basis}")
              
        return basis

class Eve:
    """ 
    Evesdropper that
    """
    def __init__(self):
        pass


class BB84:

    def __init__(self, alice: Alice, bob: Bob):
        self.alice = alice
        self.bob = bob
        
        if bob.length != alice.length:
            raise Exception("Bob's basis needs to be the same length as Alice's key.")

    def quantum_encoding(self, key:str, basis:str)->str:
        
        quantum_state = ""

        for bit,base in zip(key, basis):
            if bit == "0" and base == "Z":
                quantum_state += "0"
                continue

            if bit == "0" and base == "X":
                quantum_state += "+"
                continue

            if bit == "1" and base == "Z":
                quantum_state += "1"
                continue

            if bit == "1" and base == "X":
                quantum_state += "-"
                continue

        return quantum_state
        
    def key_sift(self):
        pass

if __name__ == "__main__":

    Alice = Alice(5)
    Bob = Bob(5)

    secret_key = Alice.rand_key()
    alice_basis = Alice.rand_basis()

    protocol = BB84(Alice, Bob)

    print(protocol.quantum_encoding(secret_key, alice_basis))