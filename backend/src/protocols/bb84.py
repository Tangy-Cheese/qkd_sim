import numpy as np
import random
from QKD_utils import error_rate, secure_key_rate, secret_fraction, binary_entropy
import json
import os

class Participants:
    """Parent class for participands of BB84 protocol. This class contains 
    attributes and methods that Alice, Bob and Eve share.

    :param length: Bit length of the sent key
    """
    def __init__(self, length:int)->None:
        """Constructor method for Participants

        :param length: Bit length of the sent key
        """
        self.length = length

    def rand_basis(self)->str:
        """The random bases needed for quantum encoding and measurments. The
        length of the random bases must be equal to that of the sent bitstring.

        :return: String representation of bases either in the Z:|0>, |1> or the 
            X:|+>, |->.
        """
        basis = ""
        bases = ["X", "Z"]
        for _ in range(self.length):
            basis += random.choice(bases)

        return basis


class Alice(Participants):
    """Alice is a participant of the BB84 protocol. Alice wants a secure key with 
    the participant Bob. Alice only needs to do two things and that is to generate a 
    random bitstring of length n, encode her bitstring by encoding each bit with a 
    random basis. And then sending the quantum states through the quantum channel.
    """
    def rand_key(self)->str:
        """Random bitstring generator

        :return: String of random 0s and 1s with some arbitrary length.
        """
        key = ""
        for _ in range(self.length):
            key += str(random.randint(0, 1))

        return key
    
    def quantum_encoding(self, key:str, basis:str)->str:
        """Encoding of bitstring into qubits

        :param key: The random bitstring (key)
        :param basis: Random basis for each bit in the bitstring
        :return: Quantum states either in the Z or X basis represented as a string.
            Each char represents a qubit where "0" = |0>. A utility function to represent
            the string of qubits in bra-ket form lies in QKD_utils.py as format_state().
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


class Bob(Participants):
    """Bob is the reciever in BB84. Bob recieves a quantum state from the channel and 
    measures each bit in some random basis. 

    :param dc_rate: The dark count rate simulates imperfect photon detection from Bob's end. 
        This value lies between 0,1. The smaller this value the more quantum states Bob can measure.
    """
    def __init__(self, length:int, dark_count_rate:float)->None:
        """Constructor method for Bob. Added attribute from Participants class.

        :param length: Length of the sent bitstring
        :param dark_count_rate: Dark count rate of Bob's detector due to imperfect
            detection.
        """
        super().__init__(length)
        self.dc_rate = dark_count_rate

    def dark_counts(self)->str:
        """Essentially, a dark count measures a photon when no detection exists. Since photons in BB84
        are measured discretely, this means every gap "_" has a chance of being measured as 0 or 1.

        :return: Either an dark count string or gap
        """
        measure = np.random.choice(("0", "1", "_"), p=(self.dc_rate/2, self.dc_rate/2, 1-self.dc_rate))
        
        #There may be an error here
        return measure

    def measurement(self, state:str, basis:str)->str:
        """Turns the quantum state back into bits through random basis measurements.

        :param state: Qubits recieved from the channel
        :param basis: Bobs random choices of basis
        :return: Bitstring of same length. Missing bits are still counted but will be sifted later
        """
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
    """Eve is also potentially a member of the BB84 protocol. In this simulation, Eve lies 
    in the quantum channel.
    """
    def _eavesdrop(self, state: str)->str:
        """Private eavesdropping method. Only Eve has this ability where inside the 
        quantum channel, she measures Alices qubits to gain information and sends 
        potentially false qubits to Bob.

        :param state: Alices qubits
        :return: Randomly encoded qubits sent to Bob, pretending to be Alice
        """
        eve_basis = self.rand_basis()
        eve_measured = Bob(self.length, 0).measurement(state, eve_basis)

        return Alice(self.length).quantum_encoding(eve_measured, eve_basis)

class Channel:
    """This Class represents the object that lies between Alice and Bob. The communication 
    network channel. 

    :param distance: The distance between two nodes in a connected QKD network. In this case,
        between Alice and Bob. Measured in Km.
    :param attenuation: This represents the photon loss due to imperfect fibre optic channels.
        Depending on the type of the fibre, it affects how many photons are lost through the channel.
    :param qber: This attribute remains empty but but is a measure of the qubit error rate between
        the two nodes. This value is stored within this class. Initialised to be empty.
    :param skr: In the same way as the qubit error rate, the secure key rate is also a measure of
        channel performance and stored here. Initialised to be empty.
    """
    def __init__(self,  eve: Eve | None, distance:int, fibre_attenuation:float)->None:
        """Class constructor

        :param eve: Eve either exists or doesnt in a quantum channel. If she does,
            then more steps within the protocol take place.
        :param distance: Distance between Alice and Bob in km.
        :param fibre_attenuation: Loss of photons between Alice and Bob due to fibre
            attenuation. 
        """
        self.eve = eve

        self.distance = distance #km
        self.attenuation = fibre_attenuation
        
        self.qber = []
        self.skr = []

    def photon_attenuation(self)->float:        
        """Converting the fibre attenuation constant into a photon survival probability

        :return: Probability of photon survival
        """
        survival_prob = pow(10,(-self.loss()/10))
        return survival_prob

    def loss(self)->float:
        """Total loss of the channel, which is what decides how good a link is.

        :return: Channel loss in dB
        """
        return self.attenuation * self.distance

    def transmit(self, state:str)->str:
        """Simulating the transmission of qubits inside of the quantum channel. Only up to two processes
        take place here. Firstly photon loss due to attenuation where a lost photon is marked by the gap 
        state "_". The second is whether eavesdropping occurs. The processes are ordered such that 
        eavesdropping always occurs before photon loss although in reality that the process is more continuous.

        :param state: Incoming qubits from Alice 
        :return: Outgoing qubits to Bob
        """
        if self.eve:
            state = self.eve._eavesdrop(state)

        photon_survival = self.photon_attenuation()
        
        channel_state = ""
        for i in state:
            channel_state += np.random.choice((i, "_"), p=(photon_survival, 1-photon_survival))

        return channel_state


class BB84:
    """Class that simulates one BB84 run between two nodes including all the participants and the channel.
    The main purpose of outputting run results between two nodes.

    :param alice: Alice partiicpant
    :param bob: Bob participant
    :param channel: Channel between Alice and Bob
    :param f_ec: Error correction efficiency. How many more bits are leaked compared
        to the ideal Shannon limit.
    """
    def __init__(self, alice: Alice, bob: Bob, channel: Channel)->None:
        """Class constructor

        :param alice: Alice participant
        :param bob: Bob Participant
        :param channel: Channel between the two
        :raises Exception: Errors if the basis, bit, key lengths are not the same
        """
        self.alice = alice
        self.bob = bob
        self.channel = channel

        if bob.length != alice.length:
            raise Exception("Bob's basis needs to be the same length as Alice's key.")

        self.f_ec = 1.15 #Arbitrary value from chatGPT... Should look a bit more into this

    def key_sift(self, key_1:str, key_2:str, basis_1:str, basis_2:str)->tuple[str, str]:
        """Key sifting process after bob measures his qubits. Alice and Bob publicly compare bases
        and sift through their keys so the remaining bits correspond to matchin bases.

        :param key_1: Alice's random bitstring
        :param key_2: Bobs measured bitstring
        :param basis_1: Alice's random encoding bases
        :param basis_2: Bob's random measuring bases
        :raises Exception: Bob and Alices key lengths must be the same or there is an error
        :return: Bob and Alice should now both have sifted keys. In an ideal world these keys would be
            identical. However, due to the possibility of Eve and for the sake of measurments, both keys 
            are stored in a tuple.
        """
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


    def error_correction(self, alice_sifted:str, qber:float)->str:
        """Error correction involves parity exchange. While we could model this, because there 
        is no error associated, we can just take the outcome of the parity exchange 
        corrections to be Alice's string.

        Steps of Error correction simplified:

        1. Key is split into blocks and the parity of each block is computed.
        2. Bob computes his parity. If the parity is the same then, they know 
        that either they have the same string, or the same number of errors.
        3. Parity block mismatch means there is certainly an error, which is 
        located using binary search. 
        4. Bob's bit is flipped to match Alice's and they would theoretically
        end up with identical strings.
        5. Permuted keys and using different block sizes etc catches all the
        errors and evens any ambiguous parity comparisons.


        :param alice_sifted: Alices sifted keys
        :param qber: Qubit error rate
        :return: Bob should have an error corrected key returned
        """ 
        n = len(alice_sifted)

        # fraction of bits leaked during EC
        leak_fraction = self.f_ec * binary_entropy(qber)
        corrected_length = max(0, int(n * (1 - leak_fraction))) #nothing left if leakage exceeds the key
       
        #Random permuation of Alice's sifted key
        arr = np.array(list(alice_sifted))
        np.random.shuffle(arr)
        permuted_key = "".join(arr)
        
        #Any slice of the randomly permuted key to remove leaked bits
        corrected_key = permuted_key[:corrected_length]

        return corrected_key

    def privacy_amplification(self, key:str, sifted_length:int, qber:float)->str:
        """Privacy amplification removes whatever Eve could have learnt about the key. In reality
        the key is hashed down to a shorter one. Like error correction, the hashing itself is not 
        modelled so the key is just shortened to the length the hash would output.

        Eve's information is bounded by the binary entropy of the qubit error rate, so 
        on top of the bits leaked by error correction, a further H(Q) of the sifted key is removed.

        :param key: Error corrected key
        :param sifted_length: Length of the sifted key before error correction
        :param qber: Qubit error rate
        :return: The final secure key
        """
        secure_length = int(sifted_length * secret_fraction(qber, self.f_ec))
        private_key = key[:secure_length]

        return private_key


    def run(self)->dict: 
        """The BB84 process is as follows:

        1) Alice Generates a secret bit key
        2) Alice Encodes her bit key onto quantum states with random bases
        3) Alice transmits them through the quantum channel
        4) Bob recieves the quantum states and measures them with random bases
        5) Alice and bob publicly compare bases and sift through matching ones
        6) Measurments are made to find the qubit error rate and secure key rate
        7) If the error rate is too high for any secure key to be left, the run is aborted
        8) Bob permutes his key to perform error correction to get an error corrected key
        9) Privacy amplification shortens the corrected key into the final secure key

        :return: A dictionary that stores all the results and variables of the simulation
        """
        secret_key = self.alice.rand_key()

        alice_basis = self.alice.rand_basis()
        alice_state = self.alice.quantum_encoding(secret_key, alice_basis)

        alice_state = self.channel.transmit(alice_state)

        bob_basis = self.bob.rand_basis()
        bob_measurment = self.bob.measurement(alice_state, bob_basis)

        sifted_keys: tuple[str, str] = self.key_sift(secret_key, bob_measurment, alice_basis, bob_basis)
        
        #Calculating error rate and key rate from the sifted keys
        err_r8 = error_rate(sifted_keys)
        sift_ratio = len(sifted_keys[0])/len(secret_key) if len(secret_key) > 0 else 0.0
        secure_key_r8 = secure_key_rate(err_r8, sift_ratio, self.f_ec)

        #No secure key can be made, either nothing arrived or Eve knows too much. So no keys are handed out
        aborted = secure_key_r8 == 0

        if aborted:
            corrected_key = ""
            secure_key = ""

        else:
            corrected_key = self.error_correction(sifted_keys[0], err_r8)
            secure_key = self.privacy_amplification(corrected_key, len(sifted_keys[0]), err_r8)

        #Python dict results
        results = {"key_length":len(secret_key),
                   
                "keys":{
                    "sifted_alice":sifted_keys[0],
                    "sifted_bob":sifted_keys[1],

                   "corrected_key":corrected_key,
                   
                   "secure_key":secure_key
                },

                "parameters":{
                    "distance_km": self.channel.distance,
                    "fibre_attenuation": self.channel.attenuation,
                    "dark_count_rate": self.bob.dc_rate  
                },

                "measurements":{
                    "shared_key_length":len(sifted_keys[0]),
                    "secure_key_length":len(secure_key),
                    "error_rate":err_r8,
                    "secure_key_rate": secure_key_r8
                },

                "aborted":aborted,

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
