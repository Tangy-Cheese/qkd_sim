from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def check():
    return {"status": "ok"}

