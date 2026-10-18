import numpy as np
from protocols.bb84 import Channel
from protocols.e91 import Alice, Bob, Eve, E91, QUANTUM_BOUND


def run(eve:bool, length:int=100000, distance:float=0, dark_count_rate:float=0)->dict:
    channel = Channel(Eve(length) if eve else None, distance, 0.2)
    return E91(Alice(length), Bob(length, dark_count_rate), channel).run()


def test_no_eve():
    """
    Without an eavesdropper or noise, the sifted keys match exactly and the
    Bell inequality is violated by the full quantum amount, |S| = 2 sqrt(2).
    """
    results = run(eve=False)

    assert results["measurements"]["error_rate"] == 0.0
    assert np.isclose(results["bell_test"]["S"], QUANTUM_BOUND, atol=0.05)
    assert not results["aborted"]


def test_eve():
    """
    Eve measuring every photon breaks the entanglement, so |S| falls below
    the classical bound of 2 and the run aborts.
    """
    results = run(eve=True)

    assert results["bell_test"]["S"] < 2
    assert results["aborted"]
    assert results["keys"]["secure_key"] == ""


def test_sift_ratio():
    """
    Only 2 of the 9 angle combinations match, so about 2/9 of the pairs are sifted.
    """
    results = run(eve=False)
    ratio = results["measurements"]["shared_key_length"] / results["key_length"]

    assert np.isclose(ratio, 2/9, atol=0.01)


def test_lossy_fibre():
    """
    Photon loss shrinks the key but does not touch the correlations of the pairs that arrive.
    """
    results = run(eve=False, distance=50, dark_count_rate=1e-3)

    assert results["bell_test"]["violated"]
    assert results["measurements"]["shared_key_length"] < 0.2 * results["key_length"]
