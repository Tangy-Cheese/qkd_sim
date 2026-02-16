import numpy as np
import random
from qkd.utils import error_rate, format_state

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
    def __init__(self, length:int):

        self.length = length

    def rand_basis(self)->str:

        basis = ""
        bases = ["X", "Z"]
        for _ in range(self.length):
            basis += random.choice(bases)

        return basis

class BB84:

    def __init__(self, alice: Alice, bob: Bob, eve: Eve):
        self.alice = alice
        self.bob = bob
        self.eve = eve

        if bob.length != alice.length:
            raise Exception("Bob's basis needs to be the same length as Alice's key.")

    def quantum_encoding(self, key:str, basis:str)->str:
        """
        Alice encodes her bitstring to quantum states using her bases.

        Parameters
        ----------
        key
            Secret key which is a string of bits.
        basis
            Alice's basis physically represents the polarisation of photon states.

        Returns
        -------
            Encoded quantum state.
        """        
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

    def eavesdropping(self, state: str)->str:
        """
        Eve attempts to gain information by measuring the quantum states
        from Alice, but because she does not know the bases, her measurements 
        disturb the states and introduce errors.

        Parameters
        ----------
        state
            Alices quantum state that she thinks has been sent to bob.

        Returns
        -------
            Eve sends off a quantum state to Bob pretending to be Alice.
        """        
        eve_basis = self.eve.rand_basis()
        eve_measurement = self.measurement(state, eve_basis)
        eve_encoded_state = self.quantum_encoding(eve_measurement, eve_basis)

        return eve_encoded_state

    def measurement(self, state:str, basis:str)->str:
        """
        Alice sends the quantum state to Bob, who measure each qubit in his randomly chosen basis.

        Parameters
        ----------
        state
            Quantum state sent from Alice.
        basis
           Bob's random basis choices.

        Returns
        -------
            If bob measures in the same state that Alice encodes her bits in, he will measure the same bit as Alice.
            However, if he measures in a different basis, then there will be a 50% chance his resulting bit is the same.
            Bob's measured state is a bitstring of same length as Alice's key.
        """        
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
        
    def key_sift(self, key_1:str, key_2:str, basis_1:str, basis_2:str)->tuple[str, str]:
        """
        Now Alice and Bob publicly compare their bases. And both their keys are sifted according to their matching bases.

        Parameters
        ----------
        key_1
            Alice's key
        key_2
            Bob's key
        basis_1
            Alice's basis string
        basis_2
            Bob's basis string

        Returns
        -------
            They each have a sifted key which keeps the bits corresponding to the position of their matching bases.

        Raises
        ------
        Exception
            Key length checks.
        """              
        str_length = len(key_1)
        if str_length != len(key_2):
            raise Exception("Keys need to be the same length when sifted.")

        sifted_alice = "".join(key_1[i] if basis_1[i] == basis_2[i] else "" for i in range(str_length))
        sifted_bob = "".join(key_2[i] if basis_1[i] == basis_2[i] else "" for i in range(str_length))

        return (sifted_alice, sifted_bob)
    
    def run(self)->tuple[str, str]:
        """_
        Running the protocol using the methods above.

        Returns
        -------
            Alice's and Bob's sifted keys.
        """        
        secret_key = self.alice.rand_key()
        alice_basis = self.alice.rand_basis()
        bob_basis = self.bob.rand_basis()
        
        state = self.quantum_encoding(secret_key, alice_basis)

        if self.eve is not None:
            state = self.eavesdropping(state)

        measured_state = self.measurement(state, bob_basis)
        sifted_keys = self.key_sift(secret_key, measured_state, alice_basis, bob_basis)

        return sifted_keys

if __name__ == "__main__":

    str_len = 1000000

    alice = Alice(str_len)
    bob = Bob(str_len)
    eve = Eve(str_len)

    protocol = BB84(alice, bob, eve)
    print(error_rate(protocol.run()))
