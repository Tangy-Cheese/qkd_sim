import pytest
from protocols.bb84 import Alice, Bob, Eve, Channel, BB84
from QKD_utils import secure_key_rate
import network as nw
import simulation as sim


def line_network():
    """
    Three nodes in a line plus one node that is not connected to anything.
    """
    a, b, c, d = nw.Node("A"), nw.Node("B"), nw.Node("C"), nw.Node("D")
    edges = [nw.Edge(a, b, 10, 0.2, None), nw.Edge(b, c, 20, 0.2, None)]

    return nw.Network([a, b, c, d], edges), (a, b, c, d)


def test_secure_key_rate_not_negative():
    assert secure_key_rate(0.0) == 1.0
    assert secure_key_rate(0.25) == 0.0
    assert secure_key_rate(0.5) == 0.0


def test_error_correction_high_qber():
    """
    When error correction leaks more bits than the key holds, nothing is left.
    """
    protocol = BB84(Alice(10), Bob(10, 0), Channel(None, 0, 0.2))

    assert protocol.error_correction("0101010101", 0.45) == ""


def test_matrixify_list():
    network, (a, b, c, d) = line_network()
    adj_mat = network.matrixify_list()

    assert adj_mat[0, 1] is adj_mat[1, 0] is network.links[0].channel
    assert adj_mat[1, 2] is network.links[1].channel
    assert adj_mat[0, 2] == 0


def test_simulation_path():
    network, (a, b, c, d) = line_network()
    result = sim.Simulation(network).run(a, c, 1000, 0)

    assert result["network"]["distance_km"] == 30
    assert result["network"]["number_of_secure_nodes"] == 1
    assert len(result["network"]["links"]) == 2


def test_simulation_bad_paths():
    network, (a, b, c, d) = line_network()
    simulation = sim.Simulation(network)

    with pytest.raises(ValueError):
        simulation.run(a, a, 1000, 0)

    with pytest.raises(ValueError):
        simulation.run(a, d, 1000, 0)


def test_secure_key_rate_falls_with_distance():
    """
    The secure key rate is per sent qubit, so photon loss must lower it.
    """
    length = 20000
    rates = []

    for distance in (0, 50):
        protocol = BB84(Alice(length), Bob(length, 0), Channel(None, distance, 0.2))
        results = protocol.run()
        rates.append(results["measurements"]["secure_key_rate"])

        assert len(results["keys"]["secure_key"]) == int(rates[-1] * length)

    assert rates[0] > 5 * rates[1] > 0


def test_no_photons_no_key():
    results = BB84(Alice(1000), Bob(1000, 0), Channel(None, 5000, 0.2)).run()

    assert results["aborted"]
    assert results["measurements"]["secure_key_rate"] == 0.0
    assert results["keys"]["secure_key"] == ""


def test_eve_aborts():
    """
    An eavesdropper on every qubit leaves no secure key, so none is handed out.
    """
    length = 20000
    results = BB84(Alice(length), Bob(length, 0), Channel(Eve(length), 0, 0.2)).run()

    assert results["aborted"]
    assert results["keys"]["corrected_key"] == ""
    assert results["keys"]["secure_key"] == ""


def test_simulation_final_key():
    """
    After the trusted node relay the root and target hold the same key.
    """
    network, (a, b, c, d) = line_network()
    result = sim.Simulation(network).run(a, c, 5000, 0)

    assert len(a.key) > 0
    assert a.key == c.key
    assert len(a.key) == result["security"]["final_key_length"] == min(len(a.sent_key), len(b.sent_key))
    assert b.received_key == a.sent_key
    assert c.received_key == b.sent_key


def test_simulation_eve_no_final_key():
    a, b, c = nw.Node("A"), nw.Node("B"), nw.Node("C")
    edges = [nw.Edge(a, b, 1, 0.2, None), nw.Edge(b, c, 1, 0.2, Eve(5000))]
    result = sim.Simulation(nw.Network([a, b, c], edges)).run(a, c, 5000, 0)

    assert a.key == c.key == ""
    assert result["security"]["secure_key_rate"] == 0.0
    assert result["security"]["final_key_length"] == 0


def test_dijkstra_avoids_worst_link():
    """
    Two short links beat one long link even though the long link has fewer hops.
    """
    a, b, c = nw.Node("A"), nw.Node("B"), nw.Node("C")
    edges = [nw.Edge(a, c, 150, 0.2, None), nw.Edge(a, b, 80, 0.2, None), nw.Edge(b, c, 80, 0.2, None)]
    network = nw.Network([a, b, c], edges)

    assert network.bfs_search(a, c) == [a, c]
    assert nw.NetAlgorithms(network).dijkstra(a, c) == [a, b, c]
    assert nw.NetAlgorithms(network).dijkstra(a, nw.Node("D")) == []


def test_add_networks():
    """
    Shared nodes are merged and of two links joining the same nodes the lower loss one is kept.
    """
    a, b = nw.Node("A"), nw.Node("B")
    b_2, c, a_2 = nw.Node("B"), nw.Node("C"), nw.Node("A")

    network_1 = nw.Network([a, b], [nw.Edge(a, b, 100, 0.2, None)])
    network_2 = nw.Network([b_2, c, a_2], [nw.Edge(b_2, c, 10, 0.2, None), nw.Edge(a_2, b_2, 50, 0.2, None)])

    combined = network_1 + network_2

    assert sorted(node.identity for node in combined.nodes) == ["A", "B", "C"]
    assert sorted(link.channel.distance for link in combined.links) == [10, 50]

    path = nw.NetAlgorithms(combined).dijkstra(combined.nodes[0], combined.nodes[-1])
    assert [node.identity for node in path] == ["A", "B", "C"]
