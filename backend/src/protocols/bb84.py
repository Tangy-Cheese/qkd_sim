import numpy as np
import random
from QKD_utils import error_rate, format_state
import json
import os

class Participants:
    
    def __init__(self, length:int):
        self.length = length

    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "Z"]
        for _ in range(self.length):
            basis += random.choice(bases)

        return basis

class Alice(Participants):

    def rand_key(self)->str:

        key = ""
        for _ in range(self.length):
            key += str(random.randint(0, 1))

        return key
    
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

class Bob(Participants):

    def measurement(self, state:str, basis:str)->str:

        measured_state = ""

        for qubit,base in zip(state,basis):
            
            coin_flip = random.randint(0, 1)

            if (qubit == "0" or qubit == "1") and base == "Z":
                measured_state += qubit
                continue

            if (qubit == "+" or qubit == "-") and base == "Z":
                measured_state += str(coin_flip)
                continue

            if (qubit == "0" or qubit == "1") and base == "X":
                measured_state += str(coin_flip)
                continue

            if (qubit == "+" or qubit == "-") and base == "X":
                measured_state += "0" if qubit =="+" else "1"
                continue
        
        return measured_state

class Eve(Participants):

    def _eavesdrop(self, state: str)->str:

        eve_basis = self.rand_basis()
        eve_measured = Bob(self.length).measurement(state, eve_basis)
        return Alice(self.length).quantum_encoding(eve_measured, eve_basis)
    
class BB84:

    def __init__(self, alice: Alice, bob: Bob, eve: Eve):
        self.alice = alice
        self.bob = bob
        self.eve = eve

        if bob.length != alice.length:
            raise Exception("Bob's basis needs to be the same length as Alice's key.")
        
    def key_sift(self, key_1:str, key_2:str, basis_1:str, basis_2:str)->tuple[str, str]:

        str_length = len(key_1)
        if str_length != len(key_2):
            raise Exception("Keys need to be the same length when sifted.")

        sifted_alice = "".join(key_1[i] if basis_1[i] == basis_2[i] else "" for i in range(str_length))
        sifted_bob = "".join(key_2[i] if basis_1[i] == basis_2[i] else "" for i in range(str_length))

        return (sifted_alice, sifted_bob)
    
    def run(self)->tuple[str, str]:

        secret_key = self.alice.rand_key()
        alice_basis = self.alice.rand_basis()
        bob_basis = self.bob.rand_basis()
        
        alice_state = alice.quantum_encoding(secret_key, alice_basis)

        if self.eve is not None:
            state = eve._eavesdrop(alice_state)

        bob_measurment = bob.measurement(state, bob_basis)
        sifted_keys = self.key_sift(secret_key, bob_measurment, alice_basis, bob_basis)

        return sifted_keys

if __name__ == "__main__":

    str_len = 1000000

    alice = Alice(str_len)
    bob = Bob(str_len)
    eve = Eve(str_len)

    protocol = BB84(alice, bob, eve)

    e_rate = error_rate(protocol.run())

    # write data as python dict
    data = {"key_length":str_len,
            "measurements":{
                "error_rate":e_rate,
                "key_rate": None
            },
            "protocol":"BB84"    
    }
    
    json_data = json.dumps(data, sort_keys=True, indent=4) #turn it into json object

    # get path to backend
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_root = os.path.dirname(backend_dir)

    #direct into output with a filename data.json
    path = os.path.join(backend_root, "output", "data.json")

    #Write the json file into the specified path and name
    with open(path, "w") as f:
        f.write(json_data)