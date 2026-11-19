# Izmjeri koliko traje dohvat pet činjenica kada zahtjeve pošalješ konkurentno.
import asyncio
import time

import httpx


async def get_cat_fact(client):
    response = await client.get("https://catfact.ninja/fact")
    return response.json()["fact"]


async def main():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        dohvati = [get_cat_fact(client) for _ in range(5)]
        facts = await asyncio.gather(*dohvati)
    for broj, fact in enumerate(facts, start=1):
        print(f"{broj}: {fact}")
    print(f"Ukupno vrijeme: {time.perf_counter() - start:.2f} s")


asyncio.run(main())
