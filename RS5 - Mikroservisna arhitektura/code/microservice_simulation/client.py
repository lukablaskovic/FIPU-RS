import asyncio, aiohttp
import time

async def fetch_service():
  async with aiohttp.ClientSession() as session:
    service_1 = session.get('http://localhost:8081/')
    service_2 = session.get('http://localhost:8082/')

    tasks = [asyncio.create_task(service_1), asyncio.create_task(service_2)]
    rezultati = await asyncio.gather(*tasks)
    
    return [await rezultat.json() for rezultat in rezultati]

async def main():
  rezultati = await fetch_service()
  
  print(rezultati)

"""    
async def main():
  print("Pokrećem main korutinu")
  start_time = time.time()
  odgovori_lista = await asyncio.gather(
    fetch_service(8081), 
    fetch_service(8082)
  )
  end_time = time.time()
  print(f"Vrijeme izvođenja je: {end_time - start_time:.2f}")
  
  print(type(odgovori_lista))
"""

asyncio.run(main())