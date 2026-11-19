# Ograniči broj aktivnih dohvata i udvostruči odgodu nakon svakog neuspjelog pokušaja.
import asyncio


async def fetch_camera_data(camera_id, semaphore):
    max_attempts = 3
    delay = 1
    response_time = 3 if camera_id == 4 else 0.5
    for attempt in range(1, max_attempts + 1):
        try:
            async with semaphore:
                print(f"Kamera {camera_id}: pokušaj {attempt}/{max_attempts}.")
                await asyncio.wait_for(asyncio.sleep(response_time), timeout=2)
                return f"Kamera {camera_id}: podaci dohvaćeni."
        except asyncio.TimeoutError:
            if attempt == max_attempts:
                return f"Kamera {camera_id}: odustajemo nakon {attempt} pokušaja."
            print(f"Kamera {camera_id}: istek vremena. Novi pokušaj za {delay} s.")
            await asyncio.sleep(delay)
            delay *= 2


async def main():
    semaphore = asyncio.Semaphore(2)
    dohvati = [fetch_camera_data(camera_id, semaphore) for camera_id in range(1, 5)]
    rezultati = await asyncio.gather(*dohvati)
    for rezultat in rezultati:
        print(rezultat)


asyncio.run(main())
