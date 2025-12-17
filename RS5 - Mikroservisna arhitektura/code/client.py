import asyncio
import aiohttp


async def fetch_fact(session):
    print("Šaljem zahtjev...")
    rezultat = await session.get("https://catfact.ninja/fact")
    return (await rezultat.json())["fact"]  # Deserijalizacija JSON odgovora


async def main():
    async with aiohttp.ClientSession() as session:
        cat_tasks = [
            asyncio.create_task(fetch_fact(session)) for _ in range(5)
        ]  # Pohranjujemo Task objekte u listu
        facts = await asyncio.gather(
            *cat_tasks
        )  # Listu raspakiravamo koristeći * operator, čekamo na rezultat izvršavanja svih Taskova
        print(facts)


asyncio.run(main())
