import numpy as np
import random

def format_state(state:str)->str:
    kets = ""
    for i in state:
        kets += f"|{i}> "

    return kets

def error_rate(keys:tuple[str,str])->float:
    a_key = keys[0]
    b_key = keys[1]
    
    if len(a_key) != len(b_key):
        raise Exception("Keys need to be the same length.")
    
    if len(a_key) == 0:
        return 0.0
    
    errors = sum(1 for i, j in zip(a_key, b_key) if i != j)
    rate = errors/len(a_key)

    return rate

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
        
    def key_sift(self, key_1:str, key_2:str)->str:
        if len(key_1) != len(key_2):
            raise Exception("Keys need to be the same length when sifted.")

        sifted_state = "".join(key_1[i] if key_1[i] == key_2[i] else "" for i in range(len(key_1)))
        return "".join("0" if (qubit == "0" or qubit == "+") else "1" for qubit in sifted_state)

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

    sifted_key = protocol.key_sift(state, measured_state)

    print(f"Their shared key is {sifted_key}")