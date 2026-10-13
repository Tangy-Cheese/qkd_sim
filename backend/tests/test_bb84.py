import pytest
from protocols.bb84 import Alice, Bob, Eve, Channel, BB84
import numpy as np


def test_no_eve():
    """
    In ideal BB84 with no eavesdropper and no noise,
    the error rate must be zero.
    """

    length = 10000  # use a large bitstring for testing

    alice = Alice(length)
    bob = Bob(length, dark_count_rate=0)
    channel = Channel(None, distance=0, fibre_attenuation=0.2)
    protocol = BB84(alice, bob, channel)

    err_rate = protocol.run()["measurements"]["error_rate"]

    assert err_rate == 0.0

def test_eve():
    """
    A BB84 protocol with an eavesdropper measuring each qubit
    has an error rate of ~25%
    """
    length = 100000  # use a large bitstring for testing

    alice = Alice(length)
    bob = Bob(length, dark_count_rate=0)
    eve = Eve(length)
    channel = Channel(eve, distance=0, fibre_attenuation=0.2)

    protocol = BB84(alice, bob, channel)
    
    err_rate = protocol.run()["measurements"]["error_rate"]

    assert np.allclose(err_rate, 0.25, atol = 1e-2)