import random
import asyncio
import aiohttp
from cctv import CCTV_frame

async def simulate_movement(seconds, frame_rate):
  coordinates = []
  for _ in range(seconds * frame_rate):

    x = random.uniform(-100, 100)
    y = random.uniform(-100, 100)
    
    coordinates.append((x, y))

    await asyncio.sleep(1 / frame_rate)
  return coordinates

async def update_camera_location(instance, x, y):
  instance.update_location(x, y)
  print(instance.info())

async def post_service1(position):
  json_data = {
    "cctv_details": {
      "location_x": position[0],
      "location_y": position[1],
      "frame_rate": 30,
      "camera_status": "Active",
      "zoom_level": 1,
      "ip_address": "192.168.5.11"
    }
  }
  async with aiohttp.ClientSession() as session:
    result = await session.post("http://localhost:8090/cctv", json=json_data)
    return await result.json()

async def post_service2(coordinate_1, coordinate_2):
  json_data = {
    "coordinates": [
      [coordinate_1[0], coordinate_1[1]],
      [coordinate_2[0], coordinate_2[1]]
    ]
  }
  async with aiohttp.ClientSession() as session:
    result = await session.post("http://localhost:8091/euclidean", json=json_data)
    return await result.json()

async def main():
  
  positions = await asyncio.gather(*[simulate_movement(i, 30) for i in range(1,6)])
  
  num_coordinates = sum(len(position) for position in positions)
  #print(num_coordinates)
  
  positions_normalized = [coordinate for position_list in positions for coordinate in position_list]
  
  lista_ntorki = []
  
  
  for position_list in positions:
    for n_torka in position_list:
      lista_ntorki.append(n_torka)

  #print(positions_normalized)
  
  first_50_positions = positions_normalized[:50]
  
  #await asyncio.gather(*[update_camera_location(camera, x, y) for (x, y) in first_50_positions])
  
  #rezultati_mc_1 = await asyncio.gather(*[asyncio.create_task(post_service1(position)) for position in first_50_positions])
  
  rezultati_mc_2 = await asyncio.gather(*[post_service2(first_50_positions[i], first_50_positions[i+1]) for i in range(0, 49, 2)])
  
  print("rezultati_mc_2", rezultati_mc_2)

if __name__ == "__main__":
  camera = CCTV_frame(1, 10, 20, 30, "Active", 1, "192.168.1.10")
  print(camera.info())
  asyncio.run(main())