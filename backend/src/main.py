from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from protocols.bb84 import Alice, Bob, Eve, Channel, BB84 
import network as nw

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
@app.post("/simulation")
def simulate(data: dict)->dict:
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

@app.post("/network")
def simulate(data: dict)->dict:
    
    """
    Might be good if we have the user add nodes to whatever format we have the network on and input node.identity as a string.
    Then, if statement only if there are >2 nodes, do we allow the creation of an edge, a butto?
    """ 
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
