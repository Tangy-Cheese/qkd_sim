import json

import numpy as np

from QKD_utils import error_rate, secure_key_rate
from protocols.bb84 import BB84, Channel

# Polarisation angles in degrees. Ekert's original angles live on the Bloch sphere,
# polarisation angles are half of those (0, pi/4, pi/2 -> 0, 22.5, 45).
ALICE_ANGLES = (0.0, 22.5, 45.0)
BOB_ANGLES = (22.5, 45.0, 67.5)

# Angle pairs used for the CHSH Bell test, (a1, b1), (a1, b3), (a3, b1), (a3, b3)
CHSH_PAIRS = ((0.0, 22.5), (0.0, 67.5), (45.0, 22.5), (45.0, 67.5))
# S = E(a1,b1) - E(a1,b3) + E(a3,b1) + E(a3,b3)
CHSH_SIGNS = (1, -1, 1, 1)

CLASSICAL_BOUND = 2.0
QUANTUM_BOUND = 2 * np.sqrt(2)


def p_opposite(angle_1:np.ndarray, angle_2:np.ndarray)->np.ndarray:
    """Chance that two photons of the singlet state give opposite results when measured
    with polarisers at angle_1 and angle_2. Equal angles always give opposite results.

    :param angle_1: Polariser angles in degrees
    :param angle_2: Polariser angles in degrees
    :return: Probability of opposite outcomes, cos^2 of the angle difference
    """
    return np.cos(np.radians(angle_1 - angle_2))**2


class Receiver:
    """Parent class for Alice and Bob in E91. Neither of them prepares anything, they each
    receive one photon of an entangled pair and measure it at a random polariser angle.

    :param length: Number of entangled pairs
    :param angles: Polariser angles this participant picks from
    """
    def __init__(self, length:int, angles:tuple[float, ...])->None:
        self.length = length
        self.angles = angles

    def rand_angles(self)->np.ndarray:
        """Random measurement angle for every pair

        :return: Array of polariser angles in degrees
        """
        return np.random.choice(self.angles, size=self.length)


class Alice(Receiver):
    """Alice sits next to the entangled photon source, so her photons never go through the fibre."""
    def __init__(self, length:int)->None:
        super().__init__(length, ALICE_ANGLES)


class Bob(Receiver):
    """Bob is at the far end of the fibre. His photons can be lost and his detector has dark counts.

    :param dark_count_rate: Chance of a click when no photon arrived
    """
    def __init__(self, length:int, dark_count_rate:float)->None:
        super().__init__(length, BOB_ANGLES)
        self.dc_rate = dark_count_rate


class Eve(Receiver):
    """Eve sits in the fibre between the source and Bob. She measures Bob's photon at a random
    angle and sends Bob a new photon polarised the way she measured. Measuring breaks the
    entanglement, so Alice and Bob end up with classical correlations that cannot break the
    Bell inequality.
    """
    def __init__(self, length:int)->None:
        super().__init__(length, BOB_ANGLES)


class E91(BB84):
    """One E91 run between two nodes. A source next to Alice makes singlet pairs
    1/sqrt(2) (|HV> - |VH>), Alice measures one photon and the other goes down the fibre to Bob.

    Error correction and privacy amplification are the same as BB84, so they are inherited.

    :param alice: Alice participant
    :param bob: Bob participant
    :param channel: Fibre between Alice and Bob, with or without an E91 Eve inside
    """
    def __init__(self, alice:Alice, bob:Bob, channel:Channel)->None:
        super().__init__(alice, bob, channel)

    def measure_pairs(self, alice_angles:np.ndarray, bob_angles:np.ndarray)->tuple[np.ndarray, np.ndarray]:
        """Measurement outcomes for every pair, before any photon loss.

        Without Eve, Alice's result is a coin flip and Bob gets the opposite result
        with probability cos^2(a - b).

        With Eve, she measures Bob's photon first at angle e and gets a coin flip.
        Alice's photon collapses to the orthogonal polarisation, so Alice gets the opposite
        of Eve with probability cos^2(a - e). Bob gets Eve's resent photon and gets the same
        result as Eve with probability cos^2(b - e).

        :param alice_angles: Alice's polariser angles
        :param bob_angles: Bob's polariser angles
        :return: Alice's and Bob's outcomes as arrays of 0s and 1s
        """
        n = len(alice_angles)
        rand = np.random.random

        if self.channel.eve is None:
            alice_bits = np.random.randint(0, 2, n)
            opposite = rand(n) < p_opposite(alice_angles, bob_angles)
            bob_bits = np.where(opposite, 1 - alice_bits, alice_bits)

        else:
            eve_angles = self.channel.eve.rand_angles()
            eve_bits = np.random.randint(0, 2, n)

            alice_opposite = rand(n) < p_opposite(alice_angles, eve_angles)
            alice_bits = np.where(alice_opposite, 1 - eve_bits, eve_bits)

            bob_same = rand(n) < p_opposite(bob_angles, eve_angles)
            bob_bits = np.where(bob_same, eve_bits, 1 - eve_bits)

        return alice_bits, bob_bits

    def transmit(self, bob_bits:np.ndarray)->str:
        """Bob's photons go through the lossy fibre. A lost photon is a gap "_" unless
        Bob's detector dark counts, which gives a random bit.

        :param bob_bits: Bob's outcomes if every photon arrived
        :return: Bob's detected bits as a string, "_" where nothing clicked
        """
        n = len(bob_bits)
        survived = np.random.random(n) < self.channel.photon_attenuation()
        dark_count = np.random.random(n) < self.bob.dc_rate
        dark_bits = np.random.randint(0, 2, n)

        return "".join(
            str(bit) if alive else (str(dark) if dark_click else "_")
            for bit, alive, dark_click, dark in zip(bob_bits, survived, dark_count, dark_bits)
        )

    def bell_test(self, alice_bits:np.ndarray, bob_bits:str,
                  alice_angles:np.ndarray, bob_angles:np.ndarray)->tuple[float, list[dict]]:
        """CHSH Bell test on the pairs measured at the four CHSH angle combinations.
        These results are announced publicly, so they are not used in the key.

        E(a, b) = P(same) - P(opposite) and S = E(a1,b1) - E(a1,b3) + E(a3,b1) + E(a3,b3).
        Entangled pairs give |S| = 2 sqrt(2), anything classical (like Eve) gives |S| <= 2.

        :return: |S| and the correlation of each angle pair
        """
        detected = np.array([b != "_" for b in bob_bits])
        bob_array = np.array([int(b) if b != "_" else -1 for b in bob_bits])

        S = 0.0
        correlations = []

        for (a, b), sign in zip(CHSH_PAIRS, CHSH_SIGNS):
            mask = detected & (alice_angles == a) & (bob_angles == b)
            pairs = int(mask.sum())
            E = float(np.mean(np.where(alice_bits[mask] == bob_array[mask], 1, -1))) if pairs else 0.0

            S += sign * E
            correlations.append({"alice_angle": a, "bob_angle": b, "correlation": E, "pairs": pairs})

        return abs(S), correlations

    def key_sift(self, alice_bits:np.ndarray, bob_bits:str,
                 alice_angles:np.ndarray, bob_angles:np.ndarray)->tuple[str, str]:
        """Keep the pairs where Bob detected something and both used the same angle.
        Those results are opposite, so Bob flips his bits to match Alice.

        :return: Alice's and Bob's sifted keys
        """
        sifted_alice = ""
        sifted_bob = ""

        for a_bit, b_bit, a_angle, b_angle in zip(alice_bits, bob_bits, alice_angles, bob_angles):
            if b_bit != "_" and a_angle == b_angle:
                sifted_alice += str(a_bit)
                sifted_bob += "1" if b_bit == "0" else "0"

        return (sifted_alice, sifted_bob)

    def run(self)->dict:
        """The E91 process is as follows:

        1) The source makes entangled pairs, one photon to Alice and one down the fibre to Bob
        2) Alice and Bob each measure at a random polariser angle
        3) They publicly announce their angles
        4) Pairs with matching angles become the sifted key, Bob flips his bits
        5) Pairs at the CHSH angles are announced and used for the Bell test
        6) If |S| <= 2 the pairs were not entangled (Eve), or the error rate leaves no key, so abort
        7) Error correction and privacy amplification as in BB84

        :return: A dictionary that stores all the results and variables of the simulation
        """
        alice_angles = self.alice.rand_angles()
        bob_angles = self.bob.rand_angles()

        alice_bits, bob_bits = self.measure_pairs(alice_angles, bob_angles)
        bob_received = self.transmit(bob_bits)

        S, correlations = self.bell_test(alice_bits, bob_received, alice_angles, bob_angles)
        sifted_keys = self.key_sift(alice_bits, bob_received, alice_angles, bob_angles)

        n_pairs = self.alice.length
        err_r8 = error_rate(sifted_keys)
        sift_ratio = len(sifted_keys[0])/n_pairs if n_pairs > 0 else 0.0
        secure_key_r8 = secure_key_rate(err_r8, sift_ratio, self.f_ec)

        bell_violated = S > CLASSICAL_BOUND
        aborted = not bell_violated or secure_key_r8 == 0

        if aborted:
            corrected_key = ""
            secure_key = ""
            secure_key_r8 = 0.0

        else:
            corrected_key = self.error_correction(sifted_keys[0], err_r8)
            secure_key = self.privacy_amplification(corrected_key, len(sifted_keys[0]), err_r8)

        return {"key_length": n_pairs,

                "keys": {
                    "sifted_alice": sifted_keys[0],
                    "sifted_bob": sifted_keys[1],
                    "corrected_key": corrected_key,
                    "secure_key": secure_key
                },

                "parameters": {
                    "distance_km": self.channel.distance,
                    "fibre_attenuation": self.channel.attenuation,
                    "dark_count_rate": self.bob.dc_rate,
                    "alice_angles": list(ALICE_ANGLES),
                    "bob_angles": list(BOB_ANGLES)
                },

                "measurements": {
                    "shared_key_length": len(sifted_keys[0]),
                    "secure_key_length": len(secure_key),
                    "error_rate": err_r8,
                    "secure_key_rate": secure_key_r8
                },

                "bell_test": {
                    "S": S,
                    "classical_bound": CLASSICAL_BOUND,
                    "quantum_bound": float(QUANTUM_BOUND),
                    "violated": bool(bell_violated),
                    "correlations": correlations
                },

                "aborted": bool(aborted),

                "protocol": "E91"
        }


if __name__ == "__main__":

    n = 100000

    for name, eve in ("clean", None), ("eve", Eve(n)):
        channel = Channel(eve, 20, 0.2)
        results = E91(Alice(n), Bob(n, 1e-3), channel).run()

        print(name, json.dumps({k: results[k] for k in ("measurements", "bell_test", "aborted")}, indent=2))
