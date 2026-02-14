import pytest
from protocols.bb84 import Alice, Bob, BB84, error_rate


def test_no_eve():
    """
    In ideal BB84 with no eavesdropper and no noise,
    the error rate must be zero.
    """

    length = 1000  # use a large bitstring for testing

    alice = Alice(length)
    bob = Bob(length)
    protocol = BB84(alice, bob, eve=None)

    alice_key = alice.rand_key()
    alice_basis = alice.rand_basis()

    bob_basis = bob.rand_basis()

    state = protocol.quantum_encoding(alice_key, alice_basis)
    bob_measured = protocol.measurement(state, bob_basis)

    alice_sifted, bob_sifted = protocol.key_sift(
        alice_key,bob_measured,
        alice_basis, bob_basis
    )

    err_rate = error_rate((alice_sifted, bob_sifted))

    assert err_rate == 0.0
