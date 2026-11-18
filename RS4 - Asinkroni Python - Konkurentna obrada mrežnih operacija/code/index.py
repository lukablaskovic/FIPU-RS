import aiohttp, asyncio


async def get_cat_fact(session):
    response = await session.get("https://catfact.ninja/fact")
    fact_dict = await response.json()
    print(fact_dict["fact"])


async def main():
    async with aiohttp.ClientSession() as session:
        cat_fact_korutine = [get_cat_fact(session) for i in range(5)]
        await asyncio.gather(*cat_fact_korutine)


if __name__ == "__main__":
    asyncio.run(main())
