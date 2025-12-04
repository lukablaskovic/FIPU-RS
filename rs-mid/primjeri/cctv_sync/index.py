import asyncio, aiohttp
import random
import cctv

async def simulate_movement(frame_rate, seconds):
  print("Generiram koordinate...", seconds)
  lista_n_torki = []
  for _ in range(frame_rate * seconds):
    pos_x = random.uniform(-100, 100)
    pos_y = random.uniform(-100, 100)
    lista_n_torki.append((pos_x, pos_y))
    await asyncio.sleep(1 / frame_rate)
  return lista_n_torki

async def update_camera_location(instance, x, y):
  instance.update_location(x, y)
  return instance.info()

async def send_request(x, y):
  
  json_data = {
    "cctv_details" : {
      "location_x": x,
      "location_y": y,
      "frame_rate": 30,
      "camera_status": "Active",
      "zoom_level": "1x",
      "ip_address": "192.168.5.11"
    }
  }
  async with aiohttp.ClientSession() as session:
    rez = await session.post("http://localhost:8090/cctv", json=json_data)
  return await rez.json()

async def send_request_2(coord1_tuple, coord_2_tuple):
  json_data = {
    "coordinates": [
      [coord1_tuple[0], coord1_tuple[1]],
      [coord_2_tuple[0], coord_2_tuple[1]]
    ]
  }
  async with aiohttp.ClientSession() as session:
    rez = await session.post("http://localhost:8091/euclidean", json=json_data)
  return await rez.json()

async def main():
  print("Pozivam main korutinu...")
  #rezultat = await simulate_movement(30, 5)
  
  positions = await asyncio.gather(*[simulate_movement(30, i) for i in range(1,6)])
  
  lista_koordinata = []
  
  for lista_ntorki in positions: # rezultat = lista koji sadrži liste
    for ntorka in lista_ntorki:
      lista_koordinata.append(ntorka)
  print("lista_koordinata", len(lista_koordinata))
  
  first_50_positions = lista_koordinata[:50]
  
  cctv_instance = cctv.CCTV_frame("1", 10, 20, 30, "Active", "1x", "192.185.5.4")
  
  lista_korutina = [update_camera_location(cctv_instance, x, y) for x, y in first_50_positions]
  
  rezultat = await asyncio.gather(*lista_korutina)
  
  rezultat = await asyncio.gather(*[send_request(x, y) for x, y in first_50_positions])
  
  #await update_camera_location(cctv_instance, koordinate[0], koordinate[1])
  
  rezultat2 = await asyncio.gather(*[send_request_2(first_50_positions[i], first_50_positions[i+1]) for i in range(0, 100, 2)])
  
  print(len(rezultat2))

asyncio.run(main())

# Korutina koja salje zahtjev sa aiohttp