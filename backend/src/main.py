from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from protocols.bb84 import Alice, Bob, Eve, Channel, BB84 
import protocols.e91

import network as nw
import simulation as sim

app = FastAPI()

#read this: https://fastapi.tiangolo.com/tutorial/cors/. 
# It will make more sense afterwards this is what allows javascript and python to interact I believe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # only allow requests from this url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Simulation route http://localhost:8000/simulation link react here
@app.post("/protocols/bb84")
def run_bb84(data: dict)->dict:
    protocol = data.get("protocol")
    key_length: int =  data.get("key_length")
    fibre_length: int = data.get("fibre_length")
    fibre_attenuation = data.get("fibre_attenuation")*10**(-3)
    eavesdropper = data.get("eve", False)

    alice = Alice(key_length)
    bob = Bob(key_length, dark_count_rate=0.08)
    eve = None 

    if eavesdropper == True:
        eve = Eve(key_length)

    channel = Channel(eve, fibre_length, fibre_attenuation)

    protocol = BB84(alice, bob, channel)
    results = protocol.run()
    
    return results #fastapi should send this as JSON

# Simulation route http://localhost:8000/simulation link react here
@app.post("/protocols/e91")
def run_e91(data: dict)->dict:
    protocol = data.get("protocol")
    key_length: int =  data.get("key_length")
    fibre_length: int = data.get("fibre_length")
    fibre_attenuation = data.get("fibre_attenuation")*10**(-3)
    eavesdropper = data.get("eve", False)

    alice = Alice(key_length)
    bob = Bob(key_length, dark_count_rate=0.08)
    eve = None 

    if eavesdropper == True:
        eve = Eve(key_length)

    channel = Channel(eve, fibre_length, fibre_attenuation)

    protocol = BB84(alice, bob, channel)
    results = protocol.run()
    
    return results #fastapi should send this as JSON


@app.post("/simulation")
def run_simulation(data: dict) -> dict:
    node_names = data.get("nodes", [])
    edge_defs = data.get("edges", [])
    root_name = data.get("root")
    target_name = data.get("target")
    key_length = int(data.get("key_length", 1000))
    dark_count_rate = float(data.get("dark_count_rate", 0.08))

    node_map = {name: nw.Node(name) for name in node_names}

    edges = []
    for e in edge_defs:
        eve = Eve(key_length) if e.get("eve") else None
        edges.append(nw.Edge(
            node_map[e["node1"]],
            node_map[e["node2"]],
            e["distance_km"],
            e["attenuation"],
            eve
        ))

    network = nw.Network(list(node_map.values()), edges)
    simulation = sim.Simulation(network)

    return simulation.run(node_map[root_name], node_map[target_name], key_length, dark_count_rate)


@app.get("/network/default")
def get_default_network() -> dict:
    return {
        "nodes": ["Alice", "Bob", "Charlie"],
        "edges": [
            {"node1": "Alice", "node2": "Bob", "distance_km": 80, "attenuation": 0.2, "eve": False},
            {"node1": "Bob", "node2": "Charlie", "distance_km": 60, "attenuation": 0.2, "eve": False}
        ]
    }
