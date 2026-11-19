# Izmjeri koliko traje dohvat pet činjenica kada svaki zahtjev čeka prethodni odgovor.
import asyncio
import time

import httpx


async def main():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        for broj in range(1, 6):
            response = await client.get("https://catfact.ninja/fact")
            print(f"{broj}: {response.json()['fact']}")
    print(f"Ukupno vrijeme: {time.perf_counter() - start:.2f} s")


asyncio.run(main())
