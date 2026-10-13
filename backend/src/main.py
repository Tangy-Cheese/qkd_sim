from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from protocols.bb84 import Alice, Bob, Eve, Channel, BB84
import protocols.e91

import network as nw
import simulation as sim

app = FastAPI()

#Chance of Bob's detector clicking when no photon arrived. Same value as the example run in protocols/bb84.py.
#Anything much higher drowns the signal after a few tens of km and every run gets aborted.
DARK_COUNT_RATE = 1e-3

#read this: https://fastapi.tiangolo.com/tutorial/cors/.
# It will make more sense afterwards this is what allows javascript and python to interact I believe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # only allow requests from this url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request bodies. FastAPI validates these and answers with a 422 if a field is missing or invalid
class ProtocolRequest(BaseModel):
    protocol: str | None = None
    key_length: int = Field(gt=0)
    fibre_length: float = Field(ge=0) #km
    fibre_attenuation: float = Field(ge=0) #in units of e-3 dB/km, as entered in the frontend form
    eve: bool = False


class EdgeRequest(BaseModel):
    node1: str
    node2: str
    distance_km: float = Field(ge=0)
    attenuation: float = Field(ge=0) #dB/km
    eve: bool = False


class SimulationRequest(BaseModel):
    nodes: list[str]
    edges: list[EdgeRequest]
    root: str
    target: str
    key_length: int = Field(default=10000, gt=0) #long links lose most photons, so short keys leave nothing to work with
    dark_count_rate: float = Field(default=DARK_COUNT_RATE, ge=0, le=1)

    @model_validator(mode="after")
    def known_nodes(self)->"SimulationRequest":
        names = set(self.nodes)

        for name in (self.root, self.target):
            if name not in names:
                raise ValueError(f"Unknown node '{name}'.")

        for edge in self.edges:
            for name in (edge.node1, edge.node2):
                if name not in names:
                    raise ValueError(f"Edge references unknown node '{name}'.")

        return self


# Simulation route http://localhost:8000/simulation link react here
@app.post("/protocols/bb84")
def run_bb84(data: ProtocolRequest)->dict:
    fibre_attenuation = data.fibre_attenuation*10**(-3)

    alice = Alice(data.key_length)
    bob = Bob(data.key_length, dark_count_rate=DARK_COUNT_RATE)
    eve = None

    if data.eve:
        eve = Eve(data.key_length)

    channel = Channel(eve, data.fibre_length, fibre_attenuation)

    protocol = BB84(alice, bob, channel)
    results = protocol.run()

    return results #fastapi should send this as JSON

# Simulation route http://localhost:8000/simulation link react here
@app.post("/protocols/e91")
def run_e91(data: ProtocolRequest)->dict:
    #protocols/e91.py is still a stub, so dont pretend by running BB84 instead
    raise HTTPException(status_code=501, detail="E91 is not implemented yet.")


@app.post("/simulation")
def run_simulation(data: SimulationRequest) -> dict:
    node_map = {name: nw.Node(name) for name in data.nodes}

    edges = []
    for e in data.edges:
        eve = Eve(data.key_length) if e.eve else None
        edges.append(nw.Edge(
            node_map[e.node1],
            node_map[e.node2],
            e.distance_km,
            e.attenuation,
            eve
        ))

    network = nw.Network(list(node_map.values()), edges)
    simulation = sim.Simulation(network)

    try:
        return simulation.run(node_map[data.root], node_map[data.target], data.key_length, data.dark_count_rate)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.get("/network/default")
def get_default_network() -> dict:
    return {
        "nodes": ["Alice", "Bob", "Charlie"],
        "edges": [
            {"node1": "Alice", "node2": "Bob", "distance_km": 80, "attenuation": 0.2, "eve": False},
            {"node1": "Bob", "node2": "Charlie", "distance_km": 60, "attenuation": 0.2, "eve": False}
        ]
    }
