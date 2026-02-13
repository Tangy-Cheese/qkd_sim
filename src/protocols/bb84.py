import numpy as np
import random

def print_state(state:str)->str:
    kets = ""
    for i in state:
        kets += f"|{i}> "

    print(kets)

class Alice:
    """
    Alice generates a random raw key and a random basis string for BB84.
    """
    def __init__(self, length:int):
        self.length = length

    def rand_key(self)->str:

        key = ""
        for _ in range(self.length):
            key += str(random.randint(0, 1))

        return key
    
    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "Z"]
        for _ in range(self.length):
            basis += random.choice(bases)
              
        return basis

class Bob:
    """ 
    Bob chooses a random basis string and later measures incoming qubits
    """
    def __init__(self, length:int):
        self. length = length

    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "Z"]
        for _ in range(self.length):
            basis += random.choice(bases)

        return basis

class Eve:
    """ 
    Eve measures each qubit in a random basis and resends the corresponding state, introducing errors.
    """
    def __init__(self):
        pass


class BB84:
    """ 
    BB84 protocol:
    1. Alices quantum encoding of the secret string
    2. Bob's measurement outcome dependent on basis choice
    3. Sifting for shared key
    """
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
    
    def measurement(self):
        pass
        
    def key_sift(self):
        pass

if __name__ == "__main__":

    Alice = Alice(5)
    Bob = Bob(5)

    secret_key = Alice.rand_key()
    alice_basis = Alice.rand_basis()

    bob_basis = Bob.rand_basis()

    print(f"Alice's key is {secret_key}")
    print(f"Alice's basis is {alice_basis}")

    print(f"Bob random basis choices are {bob_basis}")
              
    protocol = BB84(Alice, Bob)
    state = protocol.quantum_encoding(secret_key, alice_basis)

    print_state(state)