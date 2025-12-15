import asyncio, aiohttp
from aiohttp import web

app = web.Application()

async def pozdrav(request):
  await asyncio.sleep(1)
  print("Pozivam GET / iz microservice_1 skripte...")
  return web.json_response({"message" : "Hello from Microservice 1"})

app.router.add_get("/", pozdrav)

web.run_app(app, port=8081)