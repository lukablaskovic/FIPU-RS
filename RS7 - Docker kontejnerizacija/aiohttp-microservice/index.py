# aiohttp-microservice/app.py
import asyncio
from aiohttp import web

proizvodi = [
    {"id": 1, "naziv": "Laptop", "cijena": 1500},
    {"id": 2, "naziv": "Miš", "cijena": 20},
    {"id": 3, "naziv": "Tipkovnica", "cijena": 50},
    {"id": 4, "naziv": "Monitor", "cijena": 300},
    {"id": 5, "naziv": "Slušalice", "cijena": 100},
]

app = web.Application()


async def get_proizvodi(request):
    return web.json_response(proizvodi)


async def add_proizvod(request):
    data = await request.json()

    if data["naziv"] in [proizvod["naziv"] for proizvod in proizvodi]:
        return web.json_response({"error": "Proizvod već postoji!"}, status=400)

    proizvod = {
        "id": proizvodi[-1]["id"] + 1,
        "naziv": data["naziv"],
        "cijena": data["cijena"],
    }
    proizvodi.append(proizvod)
    return web.json_response(proizvod)


app.router.add_routes(
    [web.get("/proizvodi", get_proizvodi), web.post("/proizvodi", add_proizvod)]
)

web.run_app(app, host="0.0.0.0", port=8080)
