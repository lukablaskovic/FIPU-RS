# Usporedi redoslijed primitka odgovora s redoslijedom rezultata koje vraća gather.
import asyncio

import aiohttp


async def get_cat_fact(session, broj):
    async with session.get("https://catfact.ninja/fact") as response:
        data = await response.json()
        print(f"Primljen odgovor {broj}: {data['fact']}")
        return data["fact"]


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(get_cat_fact(session, broj)) for broj in range(1, 6)]
        facts = await asyncio.gather(*tasks)

    print("Rezultati u listi:")
    for broj, fact in enumerate(facts, start=1):
        print(f"{broj}: {fact}")


asyncio.run(main())
