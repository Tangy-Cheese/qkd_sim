from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from protocols.bb84 import Alice, Bob, Eve, Channel, BB84, error_rate

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
    length = data.get("length")
    eavesdropper = data.get("eve", False)

    alice = Alice(length)
    bob = Bob(length)
    eve = None 

    if eavesdropper == True:
        eve = Eve(length)

    channel = Channel(eve, 122, 0.2)

    protocol = BB84(alice, bob, channel)
    results = protocol.run()
    
    return results #fastapi should send this as JSON