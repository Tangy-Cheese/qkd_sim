import pytest
from qkd.protocols.bb84 import Alice, Bob, Eve, BB84, error_rate
import numpy as np


def test_no_eve():
    """
    In ideal BB84 with no eavesdropper and no noise,
    the error rate must be zero.
    """

    length = 10000  # use a large bitstring for testing

    alice = Alice(length)
    bob = Bob(length)
    protocol = BB84(alice, bob, eve=None)

    err_rate = error_rate(protocol.run())

    assert err_rate == 0.0

def test_eve():
    """
    A BB84 protocol with an eavesdropper measuring each qubit
    has an error rate of ~25%
    """
    length = 100000  # use a large bitstring for testing

    alice = Alice(length)
    bob = Bob(length)
    eve = Eve(length)

    protocol = BB84(alice, bob, eve)
    
    err_rate = error_rate(protocol.run())

    assert np.allclose(err_rate, 0.25, rtol = 1e-2)