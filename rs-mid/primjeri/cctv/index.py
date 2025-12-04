import random
import asyncio
async def simulate(frame_Rate, seconds):
  lista_koordinata = []
  for i in range(150):
    x = random.uniform(-100, 100)
    y = random.uniform(-100, 100)
    lista_koordinata.append((x,y))
    await asyncio.sleep(1 / frame_Rate)

  return # [(12.2343, 56.3434), (12.23, 54.54)]


asyncio.gather(*[simulate(30, i) for i in range(1,6)])

camera = CCTV_frame(1, 10, 20, 30, "Active", 1, "192.168.1.10")

async def update_camera_location(instance, x, y):
  instance.azuriraj(x, y)
  print(instance.info())
  
positions = []

import asyncio, aiohttp

async def main():
  async with aiohttp.ClientSession() as session:
    # GET - session.get()
    # POST - session.post()
    odgovor = await session.post("http://localhost:8090", json= {})
    podaci = await odgovor.json()
    print(podaci)
asyncio.run(main())