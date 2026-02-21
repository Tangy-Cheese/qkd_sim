from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from protocols.bb84 import Alice, Bob, Eve, BB84, error_rate

app = FastAPI()

#read this: https://fastapi.tiangolo.com/tutorial/cors/. 
# It will make more sense afterwards this is what allows javascript and python to interact I believe
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # only allow requests from this url
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

    simulate = BB84(alice, bob, eve)

    e_rate = error_rate(simulate.run())

    # write data as python dict
    result = {
        "protocol":"BB84",
        "key_length":length,
            "measurements": {
                "error_rate":e_rate,
                "key_rate": None
            }   
    }
    
    return result #fastapi should send this as JSON