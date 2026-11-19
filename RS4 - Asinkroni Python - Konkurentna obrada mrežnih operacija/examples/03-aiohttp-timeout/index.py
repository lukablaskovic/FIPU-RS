# Ograniči vrijeme za dohvat i čitanje jedne činjenice na deset sekundi.
import asyncio

import aiohttp


async def get_cat_fact(session):
    async with session.get("https://catfact.ninja/fact") as response:
        data = await response.json()
        return data["fact"]


async def main():
    async with aiohttp.ClientSession() as session:
        try:
            fact = await asyncio.wait_for(get_cat_fact(session), timeout=10)
            print(fact)
        except asyncio.TimeoutError:
            print("Isteklo je vrijeme za dohvat činjenice.")


asyncio.run(main())
