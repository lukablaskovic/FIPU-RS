# Pošalji jedan GET-zahtjev i pročitaj činjenicu iz JSON-odgovora.
import asyncio

import requests


async def main():
    response = requests.get("https://catfact.ninja/fact")
    print(f"HTTP status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(data["fact"])


asyncio.run(main())
