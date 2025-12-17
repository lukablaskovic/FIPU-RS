import asyncio
from aiohttp.web import AppRunner, TCPSite
from aiohttp import web, ClientSession

app = web.Application()


async def handler_function(request):
    print("Obrađujem zahtjev...")
    return web.json_response({"korisnici": ["Marko", "Pero", "Slavko"]})


app.router.add_get("/", handler_function)
host = "localhost"
port = "3030"


async def random_background_task():
    while True:
        print("1. Background task: obrađujem podatke iz reda...")
        await asyncio.sleep(5)


async def start_server():
    runner = AppRunner(app)
    await runner.setup()
    site = TCPSite(runner, host, port)
    await site.start()
    print(f"2. Poslužitelj sluša na http://{host}:{port}")


async def main():

    asyncio.create_task(random_background_task())

    asyncio.create_task(start_server())

    async with ClientSession() as session:
        print("3. Otvaram klijentsku sesiju...")
        rezultat = await session.get(f"http://{host}:{port}/")
        json_rezultat = await rezultat.json()
        print("JSON odgovor:", json_rezultat)

    await asyncio.Event().wait()


asyncio.run(main())
