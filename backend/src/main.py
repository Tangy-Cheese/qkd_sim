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
def run_simulation(data: dict)->dict:
    
    return results #fastapi should send this as JSON
