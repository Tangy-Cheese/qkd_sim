import numpy as np
import random
from QKD_utils import error_rate, secure_key_rate
import json
import os

class Participants:
    
    def __init__(self, length:int)->None:
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

    def __init__(self, length:int, dark_count_rate:float)->None:

        super().__init__(length)
        self.dc_rate = dark_count_rate

    def dark_counts(self)->str:
        measure = np.random.choice(("0", "1", "_"), p=(self.dc_rate/2, self.dc_rate/2, 1-self.dc_rate))

        return measure

    def measurement(self, state:str, basis:str)->str:

        measured_state = ""

        for qubit,base in zip(state,basis):
                
            if qubit == "_":
                measured_state += self.dark_counts()
                continue

            else:
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
        eve_measured = Bob(self.length, 0).measurement(state, eve_basis)

        return Alice(self.length).quantum_encoding(eve_measured, eve_basis)

class Channel:

    def __init__(self,  eve: Eve, distance:int, fibre_attenuation=float)->None:

        self.eve = eve
        self.distance = distance #km
        self.attenuation = fibre_attenuation

    def photon_attenuation(self)->float:        
        survival_prob = pow(10,((-self.attenuation * self.distance)/10))
        return survival_prob

    def transmit(self, state:str)->str:
        if self.eve:
            state = self.eve._eavesdrop(state)

        photon_survival = self.photon_attenuation()
        
        channel_state = ""
        for i in state:
            channel_state += np.random.choice((i, "_"), p=(photon_survival, 1-photon_survival))

        return channel_state

class BB84:

    def __init__(self, alice: Alice, bob: Bob, channel: Channel)->None:
        self.alice = alice
        self.bob = bob
        self.channel = channel

        if bob.length != alice.length:
            raise Exception("Bob's basis needs to be the same length as Alice's key.")
        
    def key_sift(self, key_1:str, key_2:str, basis_1:str, basis_2:str)->tuple[str, str]:

        str_length = len(key_1)
        if str_length != len(key_2):
            raise Exception("Keys need to be the same length when sifted.")
                
        sifted_alice = "".join(
            key_1[i] 
            for i in range(str_length)
            if key_2[i] != "_" and basis_1[i] == basis_2[i]
        )

        sifted_bob = "".join(
            key_2[i] 
            for i in range(str_length)
            if key_2[i] != "_" and basis_1[i] == basis_2[i]
        )

        return (sifted_alice, sifted_bob)
    
    def run(self)->dict:
        
        #Alice generates secret bit key
        secret_key = self.alice.rand_key()

        #Alice encodes her bit key onto quantum states with random Bases
        alice_basis = self.alice.rand_basis()
        alice_state = self.alice.quantum_encoding(secret_key, alice_basis)

        #Alice transmits them through the quantum channel
        alice_state = self.channel.transmit(alice_state)

        #Bob recieves the quantum states and measures them with random bases
        bob_basis = self.bob.rand_basis()
        bob_measurment = self.bob.measurement(alice_state, bob_basis)

        #Alice and bob publically compare bases and sift through matching ones
        sifted_keys: tuple[str, str] = self.key_sift(secret_key, bob_measurment, alice_basis, bob_basis)
        
        #Calculating error rate and key rate from the sifted keys
        err_r8 = error_rate(sifted_keys)
        secure_key_r8 = secure_key_rate(err_r8)

        #Python dict results
        results = {"key_length":len(secret_key),
                   
                "keys":{
                    "sifted_alice":sifted_keys[0],
                    "sifted_bob":sifted_keys[1]
                },

                "parameters":{
                    "distance_km": self.channel.distance,
                    "fibre_attenuation": self.channel.attenuation,
                    "dark_count_rate": self.bob.dc_rate  
                },

                "measurements":{
                    "shared_key_length":len(sifted_keys[0]),
                    "error_rate":err_r8,
                    "secure_key_rate": secure_key_r8
                },

                "protocol":"BB84"    
        }   
    
        return results

if __name__ == "__main__":

    str_len = 100000

    alice = Alice(str_len)
    bob = Bob(str_len, 1e-3)
    eve = Eve(str_len)
    
    #without eve
    channel_clean = Channel(None, 122, 0.2)
    protocol_clean = BB84(alice, bob, channel_clean)
    results_clean = protocol_clean.run()

    # with eve
    channel_eavesdropper = Channel(eve, 122, 0.2)
    protocol_eavesdropper = BB84(alice, bob, channel_eavesdropper)
    results_eavesdropper = protocol_eavesdropper.run()

    for i,j in ("clean", results_clean), ("eve", results_eavesdropper):

        json_data = json.dumps(j, sort_keys=True, indent=4) #turn it into json object

        # get path to backend
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backend_root = os.path.dirname(backend_dir)

        #direct into output with a filename data.json
        path = os.path.join(backend_root, "output", f"{i}.json")

        #Write the json file into the specified path and name
        with open(path, "w") as f:
            f.write(json_data)