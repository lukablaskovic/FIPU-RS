# Obradi istek vremena i prekid veze za svaku kameru zasebno.
import asyncio


async def fetch_camera_data(camera_id):
    if camera_id == 3:
        raise ConnectionError("Kamera je nedostupna.")
    await asyncio.sleep(camera_id)
    return "Podaci dohvaćeni."


async def ocitaj_kameru(camera_id):
    try:
        return await asyncio.wait_for(fetch_camera_data(camera_id), timeout=1.5)
    except asyncio.TimeoutError:
        return "Isteklo je vrijeme za dohvat."
    except ConnectionError as error:
        return str(error)


async def main():
    dohvati = [ocitaj_kameru(camera_id) for camera_id in range(1, 4)]
    rezultati = await asyncio.gather(*dohvati)
    for camera_id, rezultat in enumerate(rezultati, start=1):
        print(f"Kamera {camera_id}: {rezultat}")


asyncio.run(main())
