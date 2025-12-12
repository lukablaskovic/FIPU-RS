import asyncio
from aiohttp import web, ClientSession


# Definicija WebSocket poslužitelja
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(f"Primljena poruka: {msg.data}")
        elif msg.type == web.WSMsgType.ERROR:
            print(f"Greška na vezi: {ws.exception()}")

    print("WebSocket veza zatvorena")
    return ws


# Pokretanje WebSocket poslužitelja koristeći AppRunner kako bismo mogli paralelno pokrenuti klijentsku sesiju
async def start_server():
    app = web.Application()
    app.router.add_get("/ws", websocket_handler)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    print("Poslužitelj pokrenut na http://localhost:8080")
    return runner


# Definicija WebSocket klijenta
async def run_client():
    async with ClientSession() as session:
        async with session.ws_connect("http://localhost:8080/ws") as ws:
            await ws.send_str("Pozdrav, WebSocket poslužitelju!")
            msg = await ws.receive()

            if msg.type == web.WSMsgType.TEXT:
                print(f"Klijent primio: {msg.data}")
            else:
                print(f"Neočekivana poruka: {msg}")


async def main():
    runner = await start_server()

    # pričekaj da se poslužitelj stabilizira
    await asyncio.sleep(0.2)

    await run_client()
    await runner.cleanup()


asyncio.run(main())
