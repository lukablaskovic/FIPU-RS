import json
from aiohttp import web, ClientSession


votes = {
    "plavi": 0,
    "crveni": 0
}

async def glasaj(request):
    data = await request.json()
    opcija = data.get('opcija')
    
    if opcija not in votes:
        return web.json_response({"status": "nepoznata opcija"}, status=400)

    votes[opcija] += 1
    return web.json_response({"status": "uspješno glasanje"}, status=200)

async def trenutni_rezultati(request):
    return web.json_response(votes)

app = web.Application()
app.router.add_post('/glasaj', glasaj)
app.router.add_get('/rezultati', trenutni_rezultati)

async def glasaj_klijent(opcija):
    async with ClientSession() as session:
        async with session.post('http://localhost:8080/glasaj', json={"opcija": opcija}) as response:
            return await response.json()

async def rezultati_klijent():
    async with ClientSession() as session:
        async with session.get('http://localhost:8080/rezultati') as response:
            return await response.json()

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    await glasaj_klijent("crveni")
    await glasaj_klijent("crveni")
    await glasaj_klijent("crveni")
    await glasaj_klijent("plavi")
    
    results = await rezultati_klijent()
    print(results)

if __name__ == '__main__':
    #import asyncio
    #asyncio.run(main())
    web.run_app(app, port=8080)