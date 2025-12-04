import random
import asyncio
from aiohttp import ClientSession

opcije = ["plavi", "crveni"]

async def glasaj_klijent(session, opcija):
    async with session.post('http://localhost:8000/glasaj', json={"opcija": opcija}) as response:
        return await response.json()

async def mirage_simulation(broj_zahtjeva=500):
    async with ClientSession() as session:
        tasks = []
        for _ in range(broj_zahtjeva):
            opcija = random.choice(opcije)
            tasks.append(glasaj_klijent(session, opcija))
        results = await asyncio.gather(*tasks)
        
        uspjesni = sum(1 for result in results if result.get("status") == "uspješno glasanje")
        neuspjesni = broj_zahtjeva - uspjesni
        
        print(f"Uspješni zahtjevi: {uspjesni}, Neuspješni zahtjevi: {neuspjesni}")

if __name__ == '__main__':
    asyncio.run(mirage_simulation(500))
