# elections/index.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

votes = {
    "plavi": 0,
    "crveni": 0
}

class Voter(BaseModel):
    ime: str
    prezime: str
    voter_id: int

class VoteRequest(BaseModel):
    opcija: str
    # glasac: Voter

@app.post("/glasaj")
async def glasaj(vote: VoteRequest):
    if vote.opcija not in votes:
        raise HTTPException(status_code=422, detail="Nepoznata opcija")
    
    votes[vote.opcija] += 1
    return {"status": "uspješno glasanje"}

@app.get("/rezultati")
async def trenutni_rezultati():
    return votes

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
