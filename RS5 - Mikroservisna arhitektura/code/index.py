from aiohttp import web
import asyncio


async def get_users(request):
    return web.json_response(
        {"korisnici": ["Ivo", "Ana", "Marko", "Maja", "Iva", "Ivan"]}
    )


# periodična obrada poruka iz reda
async def process_messages():
    while True:
        print("Obrađujem poruke iz reda...")
        await asyncio.sleep(5)


async def start_server():
    app = web.Application()
    app.router.add_get("/korisnici", get_users)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()
    print("Poslužitelj sluša na http://localhost:8080")


async def main():
    asyncio.create_task(
        process_messages()
    )  # U event loop dodajemo korutinu koja započinje obradu dolazećih poruka
    asyncio.create_task(start_server())  # Pokrećemo poslužitelj


asyncio.run(main())  # Pokrećemo event loop
