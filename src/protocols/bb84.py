import numpy as np
import random

def format_state(state:str)->str:
    kets = ""
    for i in state:
        kets += f"|{i}> "

    return kets

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
    
    def measurement(self, state:str, basis:str)->str:
        
        measured_state = ""
        coin_flip = random.randint(0, 1)

        for qubit,base in zip(state,basis):
            if (qubit == "0" or qubit == "1") and base == "Z":
                measured_state += qubit
                continue

            if (qubit == "+" or qubit == "-") and base == "Z":
                next_bit = "0" if coin_flip == 0 else "1"
                measured_state += next_bit
                continue

            if (qubit == "0" or qubit == "1") and base == "X":
                next_bit = "+" if coin_flip == 0 else "-"
                measured_state += next_bit
                continue

            if (qubit == "+" or qubit == "-") and base == "X":
                measured_state += qubit
                continue
        
        return measured_state
        
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

    print(f"Bob's random basis choices are {bob_basis}")
              
    protocol = BB84(Alice, Bob)
    state = protocol.quantum_encoding(secret_key, alice_basis)

    print(f"Alice sends {format_state(state)} to Bob")

    measured_state = protocol.measurement(state, bob_basis)
    
    print(f"Bob measures the state and gets {format_state(measured_state)}")