# Postavi jedan rok za sve kamere i prati koje su stigle odgovoriti prije isteka.
import asyncio


async def fetch_camera_data(camera_id):
    await asyncio.sleep(camera_id)
    print(f"Kamera {camera_id}: podaci dohvaćeni.")


async def main():
    dohvati = [fetch_camera_data(camera_id) for camera_id in range(1, 4)]
    try:
        await asyncio.wait_for(asyncio.gather(*dohvati), timeout=2.5)
    except asyncio.TimeoutError:
        print("Isteklo je vrijeme za skup kamera.")


asyncio.run(main())
